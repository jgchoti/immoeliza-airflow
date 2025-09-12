import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from utils.config import ALL_KEYS
from psycopg2.extras import execute_values

class Output:
    _shared_hook = None

    def __init__(self, postgres_conn_id='postgres_default'):
        self.table_name = "zimmo_data"
        self.columns = ["zimmo_code", "type", "sub_type", "price", "street", "number",
                        "postcode", "city", "living_area_m2", "ground_area_m2",
                        "bedroom", "bathroom", "garage", "garden", "epc_kwh_m2",
                        "renovation_obligation", "year_built", "mobiscore",
                        "url", "scraped_at"]
        if Output._shared_hook is None:
            Output._shared_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        self.postgres_hook = Output._shared_hook

    def save_to_db(self, data: dict, table_name='zimmo_data'):
        if not data:
            print("No data to save")
            return

        rows = []
        for zimmo_code, row in data.items():
            if 'zimmo_code' not in row:
                row['zimmo_code'] = zimmo_code
            row = {col: row.get(col) for col in self.columns}
            rows.append(row)
            
        if not rows:
            print("No rows to insert")
            return

        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(self.columns)})
        VALUES %s
        ON CONFLICT (zimmo_code) DO UPDATE SET
            {', '.join([f"{col}=EXCLUDED.{col}" for col in self.columns if col != "zimmo_code"])}
        """
        print(insert_query)

        try:
            values = [tuple(row[col] for col in self.columns) for row in rows]
     
            conn = self.postgres_hook.get_conn()
            with conn, conn.cursor() as cur:
                template = '(' + ','.join(['%s'] * len(self.columns)) + ')'
                
                chunk_size = 500
                for i in range(0, len(values), chunk_size):
                    chunk = values[i:i+chunk_size]
                    execute_values(cur, insert_query, chunk, template=template)
            print(f"Saved {len(values)} rows to table '{table_name}' (bulk)")
        except Exception as e:
            print(f"Error saving to database: {e}")
            raise
        
    def exists(self, zimmo_code: str, table_name='zimmo_data') -> bool:
        query = f"SELECT 1 FROM {table_name} WHERE zimmo_code = %s LIMIT 1;"
        try:
            param = (str(zimmo_code),)
            result = self.postgres_hook.get_first(sql=query, parameters=param)
            return result is not None
        except Exception as e:
            print(f"❌ Error checking existing zimmo_code {zimmo_code}: {e}")
            return False
        
    def deduplicate(self, table_name=None, unique_col="zimmo_code"):
        if table_name is None:
            table_name = self.table_name
        
        query = f"""
        DELETE FROM {table_name} a
        USING {table_name} b
        WHERE a.ctid < b.ctid
          AND a.{unique_col} = b.{unique_col};
        """
        try:
            self.postgres_hook.run(query)
            print(f"✅ Deduplicated table '{table_name}' on column '{unique_col}'")
        except Exception as e:
            print(f"❌ Deduplication failed: {e}")
            raise

    def read_db(self, table_name=None, limit=None):
        if table_name is None:
            table_name = self.table_name
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        try:
 
            try:
                df = self.postgres_hook.get_pandas_df(query)
                return df
            except Exception:

                records = self.postgres_hook.get_records(query)
                column_query = f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position;
                """
                column_records = self.postgres_hook.get_records(column_query)
                columns = [row[0] for row in column_records]
                df = pd.DataFrame(records, columns=columns)
                return df
        except Exception as e:
            print(f"❌ Reading DB failed: {e}")
            raise
    
    def save_summary_to_db(self, summary_data):
        try:
            summary_row = [
                summary_data.get('category_type', 'unknown'),
                summary_data.get('total_properties', 0),
                summary_data.get('price_ranges_scraped', 0),
                summary_data.get('duration', 0),
            ]


            query = """
            INSERT INTO scrape_summary (
                category_type, total_properties, price_ranges_scraped, duration_seconds
            ) VALUES (%s, %s, %s, %s)
            """
            self.postgres_hook.run(query, parameters=summary_row)
            print(f"📊 Saved summary to scrape_summary table: {summary_row}")
        
        except Exception as e:
            print(f"❌ Failed to save summary: {e}")

