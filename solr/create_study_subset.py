import json

with open('docker/data/spongebob.json', 'r', encoding='utf-8') as f:
    episodes = json.load(f)

selected_titles = [
    # Spongebob learns to drive
    "Boating School", 
    "Pizza Delivery",
    "Hall Monitor",
    "Procrastination",
    "The Bully",
    "Doing Time",
    "New Student Starfish",
    "SquidBob TentaclePants",
    "Mrs. Puff, You're Fired",
    "Driven to Tears",
    "Boat Smarts",
    "Nautical Novice",
    "Gone",
    "Boating Buddies",
    "Ditchin'",
    "The Hot Shot",
    # Spongebob and squidward are friendly" 
    "Pizza Delivery", 
    "Nature Pants", 
    "SB-129", 
    "Bossy Boots", 
    "Dying for Pie", 
    "Pressure", 
    "Band Geeks", 
    "Krab Borg", 
    "The Camping Episode", 
    "Krusty Towers", 
    "Best Day Ever", 
    "The Two Faces of Squidward", 
    "House Fancy", 
    "Not Normal", 
    "Boating Buddies", 
    # "Spongebob parents" 
    "Ma and Pa's Big Hurrah", 
    "A SquarePants Family Vacation", 
    "Momageddon", 
    "Sheldon SquarePants", 
    "New Digs", 
    "Culture Shock", 
    "Truth or Square", 
    "SpongeBob's Big Birthday Blowout", 
    "Sing a Song of Patrick", 
    "No Free Rides", 
    # "Christmas specials" 
    "Christmas Who?",
    "It's a SpongeBob Christmas!",
    "Goons on the Moon",
    "Plankton's Old Chum",
    "SpongeBob's Road to Christmas",
    "Sandy's Country Christmas",
    "The Ho! Ho! Horror!",
    "Just in Time for Christmas"
]

filtered_episodes = [episode for episode in episodes if episode['title'] in selected_titles]

with open('docker/data/study_subset.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_episodes, f, ensure_ascii=False, indent=4)
