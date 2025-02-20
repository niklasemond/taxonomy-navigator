Taxonomy Navigator

An interactive web application for exploring and filtering hierarchical taxonomy data. Built with Dash and Bootstrap.

Features
 - Interactive navigation tree for exploring categories and subcategories
 - Detailed information display for each subcategory
 - Multiple filtering options:
   - Classification Types (CF, E, A, EU)
   - TRL Levels (TRL 1-3 through TRL 9)
 - Active filters display
 - Clear filters functionality

Installation
Clone the repository:
```
git clone https://github.com/yourusername/taxonomy-navigator.git
cd taxonomy-navigator
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

Usage

1. Run the application:
```
python src/tax_tree.py
```

2. Open your browser and navigate to:
```
http://localhost:8050
```

3. Explore the navigation tree and filter options.

Data Structure:
The taxonomy data is stored in hierarchical_tax_with_descriptions.json.

Example:
```
{
    "Category": {
        "Subcategories": {
            "Subcategory": {
                "Classification": "Type",
                "Supply Chain Classification": "Type",
                "TRL-Based Classification": "Level",
                "Description": "Text"
            }
        },
        "Description": "Category description"
    }
}
```

License
MIT License

Copyright (c) 2025 Niklas Emond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

Accessing the Taxonomy Navigator

1. Install SSH client:
   - Windows: Download and install PuTTY from https://putty.org
   - Mac/Linux: SSH client is pre-installed

2. Set up SSH tunnel:
   Windows (PuTTY):
   1. Open PuTTY
   2. Enter host: [your_ip_address]
   3. Go to Connection > SSH > Tunnels
   4. Source port: 8050
   5. Destination: localhost:8050
   6. Click "Add"
   7. Click "Open"
   8. Login with your SSH credentials

   Mac/Linux:
   1. Open Terminal
   2. Run: ssh -L 8050:localhost:8050 [username]@[your_ip_address]
   3. Enter SSH password when prompted

3. Access the application:
   1. Open web browser
   2. Go to: http://localhost:8050
   3. Login credentials:
      Username: admin
      Password: [your_chosen_password]

For support, contact: [your_contact_info]