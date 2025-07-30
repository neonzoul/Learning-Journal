# This code is generated from AI Github Copilot. press (ctrl+atl I)
# - Agent mode 
# - Model Sonnet 4.0

import json
import csv
from pathlib import Path

def extract_product_data(json_file_path, output_csv_path):
    """
    Extract product data from raw JSON and save to CSV
    """
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Navigate to the products array
        products = data['pageProps']['productListData']['products']
        
        # Define the fields we want to extract
        extracted_data = []
        
        for product in products:
            # Skip if product doesn't have required fields
            if not isinstance(product, dict) or 'name' not in product:
                continue
                
            product_info = {
                'sku': product.get('sku', ''),
                'name': product.get('name', ''),
                'price': product.get('price', ''),
                'discount': product.get('discount', ''),
                'brand': product.get('brand', ''),
                'model': product.get('model', ''),
                'min_price': product.get('minPrice', ''),
                'max_price': product.get('maxPrice', ''),
                'discount_percent': product.get('discountPercent', 0),
                'product_code': product.get('prCode', ''),
                'slug_name': product.get('slugname', ''),
                'unit_name': product.get('unitName', ''),
                'qty': product.get('qty', 0),
                'algposition': product.get('algposition', 0)
            }
            
            extracted_data.append(product_info)
        
        # Save to CSV
        if extracted_data:
            fieldnames = extracted_data[0].keys()
            
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(extracted_data)
            
            print(f"Successfully extracted {len(extracted_data)} products to {output_csv_path}")
            return extracted_data
        else:
            print("No product data found in the JSON file")
            return []
            
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return []
    except KeyError as e:
        print(f"Error: Missing key in JSON structure: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def display_sample_data(data, num_samples=3):
    """
    Display sample of extracted data
    """
    if not data:
        print("No data to display")
        return
    
    print(f"\nSample of extracted data (showing first {min(num_samples, len(data))} items):")
    print("-" * 80)
    
    for i, product in enumerate(data[:num_samples]):
        print(f"\nProduct {i+1}:")
        for key, value in product.items():
            print(f"  {key}: {value}")

def main():
    # File paths
    json_file = Path("raw_data.json")
    csv_file = Path("products_data.csv")
    
    # Extract data
    extracted_products = extract_product_data(json_file, csv_file)
    
    # Display sample
    display_sample_data(extracted_products, 3)
    
    # Print summary
    if extracted_products:
        print(f"\nSummary:")
        print(f"Total products extracted: {len(extracted_products)}")
        print(f"Output file: {csv_file}")
        
        # Show available brands
        brands = set(product['brand'] for product in extracted_products if product['brand'])
        if brands:
            print(f"Brands found: {', '.join(sorted(brands))}")

if __name__ == "__main__":
    main()