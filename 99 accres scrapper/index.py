from firecrawl import FirecrawlApp
import os
import json
import time
from pathlib import Path

# Initialize the Firecrawl client
app = FirecrawlApp(api_key='fc-737ea0737028418b8a7ea1ba1becf582')

# Create a directory to store the HTML files
output_dir = "Budget"
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Loop through the pages
for i in range(0, 100):
    # Fix the variable name from 'no' to 'i'
    time.sleep(5)
#     url = f"https://www.99acres.com/resale-ready-to-move-flats-apartments-in-gurgaon-ffid-page-{i}"
    url= "https://www.99acres.com/resale-ready-to-move-flats-apartments-in-gurgaon-75-lakhs-to-1-crore-ffid-page-{i}"
    try:
        # Scrape the URL
        response = app.scrape_url(url, params={
            'formats': ['html'],
        })
        
        # Check if the scraping was successful
        if response and 'html' in response:
            # Save the HTML content to a file
            with open(f"{output_dir}/page_{i}.html", "w", encoding="utf-8") as f:
                f.write(response['html'])
            
            # Optionally, save metadata or full response as JSON
            with open(f"{output_dir}/page_{i}_metadata.json", "w", encoding="utf-8") as f:
                json.dump(response['metadata'], f, indent=2)
                
            print(f"Successfully saved page {i}")
        else:
            print(f"Failed to scrape page {i}: No HTML content found")
    
    except Exception as e:
        print(f"Error scraping page {i}: {str(e)}")





from bs4 import BeautifulSoup
import csv
import re

def convert_price_to_int(price_text):
    """Convert price text (e.g., '₹1.75 Cr', '₹92 Lac') to integer value in rupees"""
    if price_text == "N/A":
        return price_text
    
    # Remove non-ASCII characters (like '竄ｹ') and replace with '₹'
    price_text = re.sub(r'[^\x00-\x7F]+', '₹', price_text)
    
    # Remove the rupee symbol '₹'
    price_text = price_text.replace('₹', '')
    
    # Convert crore to integer
    if 'Cr' in price_text:
        value = float(price_text.split('Cr')[0].strip())
        return int(value * 10000000)  # 1 Crore = 10,000,000
    
    # Convert lac to integer
    elif 'Lac' in price_text:
        value = float(price_text.split('Lac')[0].strip())
        return int(value * 100000)  # 1 Lac = 100,000
    
    return price_text

def convert_price_per_sqft_to_int(price_sqft_text):
    """Convert price per sqft text (e.g., '₹13,440 /sqft') to integer value"""
    if price_sqft_text == "N/A":
        return price_sqft_text
    
    # Remove non-ASCII characters (like '竄ｹ') and replace with '₹'
    price_sqft_text = re.sub(r'[^\x00-\x7F]+', '₹', price_sqft_text)
    
    # Remove the rupee symbol '₹' and '/sqft'
    price_sqft_text = price_sqft_text.replace('₹', '').replace('/sqft', '')
    
    # Remove comma and convert to integer
    try:
        return int(price_sqft_text.replace(',', '').strip())
    except ValueError:
        return price_sqft_text

def extract_property_details(html_file_path):
    """Extract property details from a saved 99acres HTML file"""
    # Read HTML from file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all property listings
    property_listings = soup.find_all('div', class_='tupleNew__outerTupleWrap')
    
    properties = []
    
    for listing in property_listings:
        try:
            # Extract property name
            property_name_elem = listing.find('div', class_='tupleNew__locationName')
            property_name = property_name_elem.text.strip() if property_name_elem else "N/A"
            
            # Extract location
            property_heading_elem = listing.find('h2', class_='tupleNew__propType')
            location = "N/A"
            if property_heading_elem:
                location_text = property_heading_elem.text
                if 'in' in location_text:
                    location = location_text.split('in')[-1].strip()
            
            # Extract price
            price_elem = listing.find('div', class_='tupleNew__priceValWrap')
            price_text = price_elem.text.strip() if price_elem else "N/A"
            price = convert_price_to_int(price_text)
            
            # Extract price per sqft
            price_sqft_elem = listing.find('div', class_='tupleNew__perSqftWrap')
            price_sqft_text = price_sqft_elem.text.strip() if price_sqft_elem else "N/A"
            price_sqft = convert_price_per_sqft_to_int(price_sqft_text)
            
            # Extract area and BHK separately
            area_wrappers = listing.find_all('div', class_='tupleNew__areaWrap')
            area = "N/A"
            bhk = "N/A"
            
            # First area wrapper typically contains the area information
            if len(area_wrappers) > 0:
                area_elem = area_wrappers[0].find('span', class_='tupleNew__area1Type')
                if area_elem:
                    area = area_elem.text.strip()
            
            # Second area wrapper typically contains the BHK information
            if len(area_wrappers) > 1:
                bhk_elem = area_wrappers[1].find('span', class_='tupleNew__area1Type')
                if bhk_elem:
                    bhk = bhk_elem.text.strip()
            
            # Extract property type/status
            type_elem = listing.find('div', class_='tupleNew__possessionBy')
            property_type = type_elem.text.strip() if type_elem else "N/A"
            
            # Extract posting time
            posted_time_elem = listing.find('div', class_='tupleNew__pbL1')
            posted_time = posted_time_elem.text.strip() if posted_time_elem else "N/A"
            
            # Extract posted by
            posted_by_elem = listing.find('div', class_='tupleNew__pbL2')
            posted_by = posted_by_elem.text.strip() if posted_by_elem else "N/A"
            
            properties.append({
                'Property Name': property_name,
                'Location': location,
                'Price': price,
                'Price per sqft': price_sqft,
                'Area': area,
                'BHK': bhk,
                'Type': property_type,
                'Posted Time': posted_time,
                'Posted By': posted_by
            })
            
        except Exception as e:
            print(f"Error extracting data from a listing: {e}")
            continue
    
    return properties

def save_to_csv(properties, filename='noida_properties2.csv'):
    """Save the extracted property data to a CSV file"""
    if not properties:
        print("No properties to save.")
        return
    
    fieldnames = [
        'Property Name', 
        'Location', 
        'Price', 
        'Price per sqft', 
        'Area',
        'BHK', 
        'Type', 
        'Posted Time', 
        'Posted By'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(properties)
    
    print(f"Successfully saved {len(properties)} properties to {filename}")

# Main execution
def main():
    # Path to the saved HTML file
    html_file_path = 'index.html'
    
    # Extract property details
    properties = extract_property_details(html_file_path)
    
    # Save to CSV
    save_to_csv(properties)
    
    # Print summary
    print(f"Extracted {len(properties)} properties")
    
    # Sample data analysis
    if properties:
        # Calculate average price
        prices = [p['Price'] for p in properties if isinstance(p['Price'], int)]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"Average property price: ₹{avg_price:,.0f}")
        
        # Calculate average price per sqft
        price_per_sqfts = [p['Price per sqft'] for p in properties if isinstance(p['Price per sqft'], int)]
        if price_per_sqfts:
            avg_price_per_sqft = sum(price_per_sqfts) / len(price_per_sqfts)
            print(f"Average price per sqft: ₹{avg_price_per_sqft:,.0f}")
        
        # Count by BHK
        bhk_counts = {}
        for p in properties:
            bhk = p['BHK']
            if bhk in bhk_counts:
                bhk_counts[bhk] += 1
            else:
                bhk_counts[bhk] = 1
        print("BHK distribution:")
        for bhk, count in bhk_counts.items():
            print(f"  {bhk}: {count}")

if __name__ == "__main__":
    main()


from bs4 import BeautifulSoup
import csv
import re
import os
from pathlib import Path

def convert_price_to_int(price_text):
    """Convert price text (e.g., '₹1.75 Cr', '₹92 Lac') to integer value in rupees"""
    if price_text == "N/A":
        return price_text
    
    # Remove non-ASCII characters (like '竄ｹ') and replace with '₹'
    price_text = re.sub(r'[^\x00-\x7F]+', '₹', price_text)
    
    # Remove the rupee symbol '₹'
    price_text = price_text.replace('₹', '')
    
    # Convert crore to integer
    if 'Cr' in price_text:
        value = float(price_text.split('Cr')[0].strip())
        return int(value * 10000000)  # 1 Crore = 10,000,000
    
    # Convert lac to integer
    elif 'Lac' in price_text:
        value = float(price_text.split('Lac')[0].strip())
        return int(value * 100000)  # 1 Lac = 100,000
    
    return price_text

def convert_price_per_sqft_to_int(price_sqft_text):
    """Convert price per sqft text (e.g., '₹13,440 /sqft') to integer value"""
    if price_sqft_text == "N/A":
        return price_sqft_text
    
    # Remove non-ASCII characters (like '竄ｹ') and replace with '₹'
    price_sqft_text = re.sub(r'[^\x00-\x7F]+', '₹', price_sqft_text)
    
    # Remove the rupee symbol '₹' and '/sqft'
    price_sqft_text = price_sqft_text.replace('₹', '').replace('/sqft', '')
    
    # Remove comma and convert to integer
    try:
        return int(price_sqft_text.replace(',', '').strip())
    except ValueError:
        return price_sqft_text

def extract_property_details(html_file_path):
    """Extract property details from a saved 99acres HTML file"""
    # Read HTML from file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all property listings
    property_listings = soup.find_all('div', class_='tupleNew__outerTupleWrap')
    
    properties = []
    
    for listing in property_listings:
        try:
            # Extract property name
            property_name_elem = listing.find('div', class_='tupleNew__locationName')
            property_name = property_name_elem.text.strip() if property_name_elem else "N/A"
            
            # Extract location
            property_heading_elem = listing.find('h2', class_='tupleNew__propType')
            location = "N/A"
            if property_heading_elem:
                location_text = property_heading_elem.text
                if 'in' in location_text:
                    location = location_text.split('in')[-1].strip()
            
            # Extract price
            price_elem = listing.find('div', class_='tupleNew__priceValWrap')
            price_text = price_elem.text.strip() if price_elem else "N/A"
            price = convert_price_to_int(price_text)
            
            # Extract price per sqft
            price_sqft_elem = listing.find('div', class_='tupleNew__perSqftWrap')
            price_sqft_text = price_sqft_elem.text.strip() if price_sqft_elem else "N/A"
            price_sqft = convert_price_per_sqft_to_int(price_sqft_text)
            
            # Extract area and BHK separately
            area_wrappers = listing.find_all('div', class_='tupleNew__areaWrap')
            area = "N/A"
            bhk = "N/A"
            
            # First area wrapper typically contains the area information
            if len(area_wrappers) > 0:
                area_elem = area_wrappers[0].find('span', class_='tupleNew__area1Type')
                if area_elem:
                    area = area_elem.text.strip()
            
            # Second area wrapper typically contains the BHK information
            if len(area_wrappers) > 1:
                bhk_elem = area_wrappers[1].find('span', class_='tupleNew__area1Type')
                if bhk_elem:
                    bhk = bhk_elem.text.strip()
            
            # Extract property type/status
            type_elem = listing.find('div', class_='tupleNew__possessionBy')
            property_type = type_elem.text.strip() if type_elem else "N/A"
            
            # Extract posting time
            posted_time_elem = listing.find('div', class_='tupleNew__pbL1')
            posted_time = posted_time_elem.text.strip() if posted_time_elem else "N/A"
            
            # Extract posted by
            posted_by_elem = listing.find('div', class_='tupleNew__pbL2')
            posted_by = posted_by_elem.text.strip() if posted_by_elem else "N/A"
            

            property_link = "N/A"
            link_elem = listing.find('a', class_='tupleNew__propertyHeading ellipsis')
            if link_elem and 'href' in link_elem.attrs:
                property_link = link_elem['href']
                # Make sure it's a full URL
                if property_link.startswith('/'):
                    property_link = 'https://www.99acres.com' + property_link

            
            image_url = "N/A"
            img_elem = listing.find('img', class_='tupleNew__imgLoader')
            if img_elem and 'src' in img_elem.attrs:
                image_url = img_elem['src']
            elif img_elem and 'data-src' in img_elem.attrs:  # Some sites use lazy loading
                image_url = img_elem['data-src']

            properties.append({
                'Property Name': property_name,
                'Location': location,
                'Price': price,
                'Price per sqft': price_sqft,
                'Area': area,
                'BHK': bhk,
                'Type': property_type,
                'Posted Time': posted_time,
                'Posted By': posted_by,
                'Property URL': property_link,
                'Image URL': image_url,
                'Page': os.path.basename(html_file_path)  # Add page info for tracking
            })
            
        except Exception as e:
            print(f"Error extracting data from a listing in {html_file_path}: {e}")
            continue
    
    return properties

def save_to_csv(properties, filename='noida_properties.csv'):
    """Save the extracted property data to a CSV file"""
    if not properties:
        print("No properties to save.")
        return
    
    fieldnames = [
        'Property Name', 
        'Location', 
        'Price', 
        'Price per sqft', 
        'Area',
        'BHK', 
        'Type', 
        'Posted Time', 
        'Posted By',
        'Property URL',
        'Image URL', 
        'Page'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(properties)
    
    print(f"Successfully saved {len(properties)} properties to {filename}")

def analyze_data(properties):
    """Perform basic analysis on the extracted property data"""
    # Calculate average price
    prices = [p['Price'] for p in properties if isinstance(p['Price'], int)]
    if prices:
        avg_price = sum(prices) / len(prices)
        print(f"Average property price: ₹{avg_price:,.0f}")
    
    # Calculate average price per sqft
    price_per_sqfts = [p['Price per sqft'] for p in properties if isinstance(p['Price per sqft'], int)]
    if price_per_sqfts:
        avg_price_per_sqft = sum(price_per_sqfts) / len(price_per_sqfts)
        print(f"Average price per sqft: ₹{avg_price_per_sqft:,.0f}")
    
    # Count by BHK
    bhk_counts = {}
    for p in properties:
        bhk = p['BHK']
        if bhk in bhk_counts:
            bhk_counts[bhk] += 1
        else:
            bhk_counts[bhk] = 1
    print("BHK distribution:")
    for bhk, count in sorted(bhk_counts.items()):
        print(f"  {bhk}: {count}")
    
    # Count by location
    location_counts = {}
    for p in properties:
        location = p['Location']
        if location in location_counts:
            location_counts[location] += 1
        else:
            location_counts[location] = 1
    
    print("\nTop 10 locations by property count:")
    for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {location}: {count}")

# Main execution
def main():
    # Directory containing the saved HTML files
    html_dir = "Budget"
    
    # Get all HTML files
    html_files = list(Path(html_dir).glob("*.html"))
    print(len(html_files))
    if not html_files:
        print(f"No HTML files found in {html_dir}")
        return
    
    print(f"Found {len(html_files)} HTML files to process")
    
    # Extract property details from all files
    all_properties = []
    for html_file in html_files:
        print(f"Processing {html_file}...")
        properties = extract_property_details(html_file)
        all_properties.extend(properties)
        print(f"  Extracted {len(properties)} properties from {html_file}")
    
    # Save all properties to CSV
    save_to_csv(all_properties, 'gurgaon_properties_all_pages.csv')
    
    # Print summary and analysis
    print(f"\nTotal properties extracted: {len(all_properties)}")
    analyze_data(all_properties)

if __name__ == "__main__":
    main()
