import duckdb, sys, importlib.util
spec = importlib.util.spec_from_file_location("brain_scoring","brain_scoring_local.py")
bs = importlib.util.module_from_spec(spec); sys.modules["brain_scoring"]=bs; spec.loader.exec_module(bs)
print("PROBABLE_CONTAMINANTS =", bs.PROBABLE_CONTAMINANTS)
import inspect
print("\n--- is_probable_contaminant source ---")
print(inspect.getsource(bs.is_probable_contaminant))

con = duckdb.connect()
con.execute("CREATE VIEW panel AS SELECT * FROM 'panel_rows.parquet'")
con.execute("CREATE VIEW idx AS SELECT * FROM 'index_events.parquet'")
orgs = con.execute("""SELECT DISTINCT p.org_name FROM panel p JOIN idx i USING (micro_specimen_id)""").df()
flag = [(o, bs.is_probable_contaminant(o)) for o in sorted(orgs.org_name)]
print(f"\ndistinct organisms at index: {len(flag)}")
print("\n=== FLAGGED AS PROBABLE CONTAMINANT ===")
for o,f in flag:
    if f: print("  ", o)
print("\n=== NOT flagged (first 40) ===")
for o,f in flag[:80]:
    if not f: print("  ", o)
