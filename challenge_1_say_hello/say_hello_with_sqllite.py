import sqlite3
import time
from datetime import datetime, timezone

pokemon_gen1 = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata",
    "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu",
    "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂",
    "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
    "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume",
    "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth",
    "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine",
    "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke",
    "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
    "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter",
    "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb",
    "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee",
    "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey",
    "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu",
    "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", "Pinsir",
    "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee", "Vaporeon",
    "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto", "Kabutops",
    "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini",
    "Dragonair", "Dragonite", "Mewtwo", "Mew"
]

def sayHello(name):
    return f"Hello, {name}. I choose you!"

def init_db(db_path="pokemon_log.db"):
    """Initializes the SQLite database and creates the execution_logs table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create logs table with primary key, indexable columns, and metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pokemon_name TEXT NOT NULL,
            message TEXT NOT NULL,
            start_time_utc TEXT NOT NULL,
            end_time_utc TEXT NOT NULL,
            duration_seconds REAL NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def main():
    db_path = "pokemon_log.db"
    init_db(db_path)

    # Establish single database connection for batch transaction processing
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    records = []

    for pokemon in pokemon_gen1:
        # 1. Capture execution metrics
        start_time_iso = datetime.now(timezone.utc).isoformat()
        start_perf = time.perf_counter()

        message = sayHello(pokemon)

        end_perf = time.perf_counter()
        end_time_iso = datetime.now(timezone.utc).isoformat()
        duration_seconds = round(end_perf - start_perf, 6)

        # 2. Stage record tuple for parameterized SQL insertion
        records.append((
            pokemon,
            message,
            start_time_iso,
            end_time_iso,
            duration_seconds
        ))

    # 3. Perform high-performance batch insert using executemany()
    cursor.executemany("""
        INSERT INTO execution_logs (
            pokemon_name, 
            message, 
            start_time_utc, 
            end_time_utc, 
            duration_seconds
        ) VALUES (?, ?, ?, ?, ?)
    """, records)

    # 4. Commit transaction and close connection
    conn.commit()
    conn.close()

    print(f"Successfully logged {len(records)} entries into SQLite database '{db_path}'")

def view_logs(db_path="pokemon_log.db", limit=5):
    """Utility function to query and display logged entries from SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM execution_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    print(f"\n--- Last {limit} Log Entries in Database ---")
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Duration: {row[5]}s | Time: {row[3]}")
        
    conn.close()

if __name__ == "__main__":
    main()
    view_logs()
