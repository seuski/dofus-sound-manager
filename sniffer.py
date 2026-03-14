"""
sniffer.py — Détection des changements de map Dofus 3 via lecture mémoire
"""

import threading
import time
import struct
from typing import Callable, Optional, List, Tuple


class MapSniffer:

    PROCESS_NAME   = "Dofus.exe"
    SCAN_INTERVAL  = 0.15
    MIN_MAP_ID     = 10_000_000
    MAX_MAP_ID     = 999_999_999

    def __init__(self, callback: Callable[[str], None], resync_callback=None, interface: str = None):
        self.callback           = callback
        self._resync_callback   = resync_callback
        self._running           = False
        self._pm                = None
        self._watch_addr        = None
        self._last_map_id       = None
        self._candidates        = []
        self._resyncing         = False  # évite les popups en boucle

    def start(self):
        self._running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._running = False

    # ── Boucle principale ────────────────────────────────────────────

    def _run(self):
        print("[Sniffer] Démarrage...")
        try:
            import pymem
        except ImportError:
            import subprocess
            subprocess.run(["pip", "install", "pymem", "--quiet"], capture_output=True)
            import pymem

        # Attendre Dofus
        while self._running:
            try:
                self._pm = pymem.Pymem(self.PROCESS_NAME)
                print(f"[Sniffer] ✓ Dofus.exe (PID {self._pm.process_id})")
                break
            except Exception:
                print("[Sniffer] En attente de Dofus.exe...")
                time.sleep(3)

        if not self._running:
            return

        # Le mapId initial est fourni par l'utilisateur via _last_map_id
        if self._last_map_id:
            print(f"[Sniffer] MapId fourni: {self._last_map_id}")
            self._scan_candidates(self._last_map_id)
            if self._candidates:
                self.callback(str(self._last_map_id))
            else:
                print(f"[Sniffer] ⚠ 0 candidats — mapId peut-être déjà changé")
                self._request_new_mapid()

        while self._running:
            if self._watch_addr:
                self._check_watch_addr()
            elif self._candidates:
                self._validate_candidates()
            elif self._last_map_id and not self._watch_addr and not self._resyncing:
                # Plus de candidats ni d'adresse — redemander le mapId
                print(f"[Sniffer] ⚠ Sniffer perdu, demande nouveau mapId...")
                self._resyncing = True
                self._request_new_mapid()
                self._resyncing = False
            time.sleep(self.SCAN_INTERVAL)

    def _auto_detect_map_id(self) -> int:
        """Scanne la mémoire pour trouver un mapId valide dans la base de données"""
        try:
            import json, os, ctypes
            from ctypes import wintypes

            # Charger la base de données
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map_database.json")
            if not os.path.exists(db_path):
                return None
            with open(db_path, encoding="utf-8") as f:
                db = json.load(f)

            db_keys = set(db.keys())
            candidates_found = {}

            # Scanner via VirtualQueryEx
            MEM_COMMIT  = 0x1000
            PAGE_NOACCESS = 0x01
            handle = self._pm.process_handle

            addr = 0
            max_addr = 0x7FFFFFFF0000

            class MEMORY_BASIC_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BaseAddress",       ctypes.c_ulonglong),
                    ("AllocationBase",    ctypes.c_ulonglong),
                    ("AllocationProtect", wintypes.DWORD),
                    ("PartitionId",       wintypes.WORD),
                    ("RegionSize",        ctypes.c_ulonglong),
                    ("State",             wintypes.DWORD),
                    ("Protect",           wintypes.DWORD),
                    ("Type",              wintypes.DWORD),
                ]

            mbi = MEMORY_BASIC_INFORMATION()
            while addr < max_addr:
                ret = ctypes.windll.kernel32.VirtualQueryEx(
                    handle, ctypes.c_ulonglong(addr),
                    ctypes.byref(mbi), ctypes.sizeof(mbi)
                )
                if not ret:
                    break
                if mbi.State == MEM_COMMIT and mbi.Protect != PAGE_NOACCESS and mbi.RegionSize > 0:
                    try:
                        data = self._pm.read_bytes(mbi.BaseAddress, min(mbi.RegionSize, 4 * 1024 * 1024))
                        for i in range(0, len(data) - 4, 4):
                            val = struct.unpack_from("<I", data, i)[0]
                            if self.MIN_MAP_ID < val < self.MAX_MAP_ID and str(val) in db_keys:
                                candidates_found[val] = candidates_found.get(val, 0) + 1
                    except Exception:
                        pass
                addr = mbi.BaseAddress + mbi.RegionSize

            if not candidates_found:
                return None

            best = max(candidates_found, key=candidates_found.get)
            print(f"[Sniffer] {len(candidates_found)} mapIds candidats, meilleur: {best} ({candidates_found[best]}x)")
            return best
        except Exception as e:
            print(f"[Sniffer] Erreur auto-détection: {e}")
            return None

    def set_mapid(self, map_id: int):
        """Appelé depuis main.py quand l'utilisateur fournit un nouveau mapId"""
        print(f"[Sniffer] Nouveau mapId reçu: {map_id}")
        self._resyncing = False
        self._last_map_id = map_id
        self._watch_addr = None
        self._candidates = []
        self._scan_candidates(map_id)
        if self._candidates:
            self.callback(str(map_id))

    def _request_new_mapid(self):
        """Demande un nouveau mapId via le callback de resynchro"""
        if self._resync_callback:
            self._resync_callback()
        # Longue pause pour laisser l'utilisateur répondre et éviter le spam
        time.sleep(30)

    # ── Scan initial ─────────────────────────────────────────────────

    def _scan_candidates(self, map_id: int, background=False):
        """Trouve toutes les adresses contenant map_id via scan ctypes direct"""
        try:
            import ctypes
            from ctypes import wintypes

            candidates = []
            MAX_CANDIDATES = 500
            pat4 = struct.pack("<I", map_id)
            pat8 = struct.pack("<Q", map_id)
            handle = self._pm.process_handle

            class MEMORY_BASIC_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BaseAddress",       ctypes.c_ulonglong),
                    ("AllocationBase",    ctypes.c_ulonglong),
                    ("AllocationProtect", wintypes.DWORD),
                    ("PartitionId",       wintypes.WORD),
                    ("RegionSize",        ctypes.c_ulonglong),
                    ("State",             wintypes.DWORD),
                    ("Protect",           wintypes.DWORD),
                    ("Type",              wintypes.DWORD),
                ]

            MEM_COMMIT    = 0x1000
            PAGE_NOACCESS = 0x01
            PAGE_GUARD    = 0x100

            mbi = MEMORY_BASIC_INFORMATION()
            addr = 0
            while addr < 0x7FFFFFFF0000 and len(candidates) < MAX_CANDIDATES:
                ret = ctypes.windll.kernel32.VirtualQueryEx(
                    handle, ctypes.c_ulonglong(addr),
                    ctypes.byref(mbi), ctypes.sizeof(mbi)
                )
                if not ret:
                    break
                if (mbi.State == MEM_COMMIT and
                    mbi.Protect & ~PAGE_GUARD not in (PAGE_NOACCESS,) and
                    0 < mbi.RegionSize <= 32 * 1024 * 1024):
                    try:
                        data = self._pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                        # Chercher pattern 4 octets
                        pos = 0
                        while True:
                            idx = data.find(pat4, pos)
                            if idx == -1:
                                break
                            candidates.append((mbi.BaseAddress + idx, 4))
                            pos = idx + 4
                            if len(candidates) >= MAX_CANDIDATES:
                                break
                        # Chercher pattern 8 octets
                        if len(candidates) < MAX_CANDIDATES:
                            pos = 0
                            while True:
                                idx = data.find(pat8, pos)
                                if idx == -1:
                                    break
                                candidates.append((mbi.BaseAddress + idx, 8))
                                pos = idx + 8
                                if len(candidates) >= MAX_CANDIDATES:
                                    break
                    except Exception:
                        pass
                addr = mbi.BaseAddress + max(mbi.RegionSize, 1)

            print(f"[Sniffer] {len(candidates)} candidats pour {map_id}")
            self._candidates = candidates[:MAX_CANDIDATES]
            if not background:
                self._watch_addr = None
        except Exception as e:
            print(f"[Sniffer] Erreur scan: {e}")

    # ── Validation : trouver la bonne adresse ────────────────────────

    def _validate_candidates(self):
        """
        Attend un vrai changement de map pour identifier quelle adresse
        est la source canonique du mapId.
        On attend que TOUTES les adresses soient stables sur la même valeur,
        puis on surveille.
        """
        if not self._candidates:
            return

        # Lire toutes les valeurs actuelles
        current = {}
        for addr, size in self._candidates:
            try:
                raw = self._pm.read_bytes(addr, size)
                val = struct.unpack("<I" if size == 4 else "<Q", raw)[0]
                if self.MIN_MAP_ID < val < self.MAX_MAP_ID:
                    current[addr] = (val, size)
            except Exception:
                pass

        if not current:
            return

        # Chercher si un changement vient de se produire
        changed = {addr: (val, size) for addr, (val, size) in current.items()
                   if val != self._last_map_id}

        if not changed:
            return  # Pas encore de changement

        # Un changement détecté — trouver la valeur majoritaire
        from collections import Counter
        vals = [val for val, size in changed.values()]
        most_common_val = Counter(vals).most_common(1)[0][0]

        # Garder uniquement les adresses avec cette valeur
        stable = [(addr, size) for addr, (val, size) in changed.items()
                  if val == most_common_val]

        if stable:
            # Choisir l'adresse avec l'index le plus bas (plus stable en général)
            self._watch_addr = sorted(stable)[0]
            self._candidates = []
            print(f"[Sniffer] ✓ Adresse fixée: 0x{self._watch_addr[0]:X} (size={self._watch_addr[1]})")
            print(f"[Sniffer] 🗺️ {self._last_map_id} → {most_common_val}")
            self._last_map_id = most_common_val
            self.callback(str(most_common_val))

    # ── Surveillance de l'adresse unique ────────────────────────────

    def _check_watch_addr(self):
        """Lit l'adresse unique et détecte les changements"""
        addr, size = self._watch_addr
        try:
            raw = self._pm.read_bytes(addr, size)
            val = struct.unpack("<I" if size == 4 else "<Q", raw)[0]

            if not (self.MIN_MAP_ID < val < self.MAX_MAP_ID):
                return

            if val != self._last_map_id:
                # Confirmer avec une 2e lecture 50ms plus tard
                time.sleep(0.05)
                raw2 = self._pm.read_bytes(addr, size)
                val2 = struct.unpack("<I" if size == 4 else "<Q", raw2)[0]
                if val2 == val and val != self._last_map_id:  # Stable et nouveau
                    self._last_map_id = val
                    self.callback(str(val))
                    print(f"[Sniffer] 🗺️ → {val}")

        except Exception as e:
            print(f"[Sniffer] Adresse perdue: {e}")
            # Rescanner seulement si vraiment perdu
            if self._last_map_id:
                self._scan_candidates(self._last_map_id)
            self._watch_addr = None


class MockSniffer:
    FAKE_MAPS = ["188745218", "75497730", "68552449", "106693122", "99615238"]

    def __init__(self, callback: Callable[[str], None], interval: float = 6.0):
        self.callback = callback
        self.interval = interval
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._running = False

    def _run(self):
        import random
        while self._running:
            time.sleep(self.interval)
            if self._running:
                self.callback(random.choice(self.FAKE_MAPS))
