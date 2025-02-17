# Taxonomy Navigator

An interactive web application for exploring and filtering hierarchical taxonomy data. Built with Dash and Bootstrap.

## Features
- Interactive navigation tree for exploring categories and subcategories
- Detailed information display for each subcategory
- Color-coded badges for Classifications and TRL levels
- Detailed descriptions of Classifications and TRL levels
- Multiple filtering options:
  - Classification Types (CF, E, A, EU)
  - TRL Levels (TRL 1-3 through TRL 9)
- Active filters display
- Clear filters functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/taxonomy-navigator.git
cd taxonomy-navigator
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python tax_tree.py
```

2. Open your browser and navigate to:
```
http://localhost:8050
```

## Data Structure

The taxonomy data is stored in `hierarchical_tax_with_descriptions.json` with the following structure:

```json
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

## License
MIT License 