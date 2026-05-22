"""Diagnostic de l'état actuel des données DMRA dans la base locale.
Usage : python scripts/dmra_check_state.py
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "db.sqlite3"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

AMOS_ID = 6
DMRA_ID = 9


def show(title, sql, params=()):
    print(f"\n=== {title} ===")
    cur.execute(sql, params)
    rows = cur.fetchall()
    if not rows:
        print("  (aucun)")
        return
    for r in rows:
        print("  " + " | ".join(f"{k}={r[k]}" for k in r.keys()))


# 1. Tous les flux impliquant AMOS
show(
    "Flux impliquant AMOS",
    """SELECT f.id, src.code as src, tgt.code as tgt, f.name, f.description, f.frequency,
              f.is_automated, f.is_critical
       FROM cartography_dataflow f
       JOIN cartography_system src ON f.source_id=src.id
       JOIN cartography_system tgt ON f.target_id=tgt.id
       WHERE f.source_id=? OR f.target_id=?
       ORDER BY f.id""",
    (AMOS_ID, AMOS_ID),
)

# 2. Hypothèses de flux liées à AMOS
show(
    "Hypothèses de flux liées à AMOS (flowfieldhypothesis)",
    """SELECT h.*
       FROM cartography_flowfieldhypothesis h
       JOIN cartography_dataflow f ON h.flow_id=f.id
       WHERE f.source_id=? OR f.target_id=?""",
    (AMOS_ID, AMOS_ID),
)

# 3. Process liés à la DMRA
show(
    "Process associés à la DMRA",
    """SELECT p.id, p.code, p.name, p.status, p.validation_status
       FROM cartography_process p
       JOIN cartography_process_structures ps ON p.id=ps.process_id
       WHERE ps.structure_id=?""",
    (DMRA_ID,),
)

# 4. Process liés à AMOS (via process_systems)
show(
    "Process associés à AMOS (process_systems)",
    """SELECT p.id, p.code, p.name
       FROM cartography_process p
       JOIN cartography_process_systems ps ON p.id=ps.process_id
       WHERE ps.system_id=?""",
    (AMOS_ID,),
)

# 5. Existe-t-il encore des flux AMOS-AGS / AMOS-Q-PULSE / AMOS-SAGESTOCK ?
print("\n=== Vérification flux supposés écartés ===")
for src_code, tgt_code in [("AMOS", "AGS"), ("AGS", "AMOS"),
                            ("AMOS", "QPULSE"), ("QPULSE", "AMOS"),
                            ("AMOS", "SAGE-STOCK"), ("SAGE-STOCK", "AMOS"),
                            ("AMOS", "SAGESTOCK"), ("SAGESTOCK", "AMOS")]:
    cur.execute(
        """SELECT f.id, f.name FROM cartography_dataflow f
           JOIN cartography_system s1 ON f.source_id=s1.id
           JOIN cartography_system s2 ON f.target_id=s2.id
           WHERE s1.code=? AND s2.code=?""",
        (src_code, tgt_code),
    )
    rows = cur.fetchall()
    status = "❌ existe" if rows else "✅ absent"
    print(f"  {src_code:12s} -> {tgt_code:12s} : {status}")
    for r in rows:
        print(f"     id={r['id']} name={r['name']}")

# 6. Description F-4 actuelle
show(
    "Détail flux F-4 (AMOS->AIMS)",
    """SELECT f.id, f.name, f.description, f.frequency, f.is_critical
       FROM cartography_dataflow f
       JOIN cartography_system src ON f.source_id=src.id
       JOIN cartography_system tgt ON f.target_id=tgt.id
       WHERE src.code='AMOS' AND tgt.code='AIMS'""",
)

# 7. F-83 description
show(
    "Détail flux F-83 (AMOS->SAGE-FIN)",
    """SELECT f.id, f.name, f.description, f.frequency, f.is_critical
       FROM cartography_dataflow f
       JOIN cartography_system src ON f.source_id=src.id
       JOIN cartography_system tgt ON f.target_id=tgt.id
       WHERE src.code='AMOS'""",
)

# 8. Liste des codes systèmes pour repérer SAGE STOCK / Q-PULSE / AGS / ERP
show(
    "Codes des systèmes SAGE/QPULSE/AGS/AMOS/AIMS/ERP",
    """SELECT id, code, name FROM cartography_system
       WHERE code IN ('AMOS','AIMS','AGS','QPULSE','Q-PULSE','SAGE-STOCK','SAGESTOCK',
                      'SAGE-FIN','SAGEFIN','ERP','ERP-AH','ERPAH','SAGE-COMPTA')
       ORDER BY code""",
)

# 9. Voir aussi tous les codes systèmes contenant SAGE
show(
    "Tous les systèmes SAGE / ERP",
    """SELECT id, code, name FROM cartography_system
       WHERE code LIKE '%SAGE%' OR code LIKE '%ERP%'
       ORDER BY code""",
)

con.close()
