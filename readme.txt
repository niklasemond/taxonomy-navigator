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