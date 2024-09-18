import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium
import re
import os  # To check if the file exists

# Set page configuration
st.set_page_config(page_title="Tourism Statistics in Lebanon", page_icon="📊", layout="wide")

# Add a title and description
st.title("Tourism Statistics in Lebanon 🇱🇧")
st.write("""
Lebanon's tourism industry is renowned for its rich history, diverse culture, and stunning landscapes. The country offers a unique blend of historical sites, beautiful coastlines, and vibrant cities. In this dashboard, you can explore various statistics related to Lebanon's tourism sector.
""")

# Load the dataset from the URL
path = "https://linked.aub.edu.lb/pkgcube/data/04c5f4bde28959f32bea81b9138bf5b3_20240905_163812.csv"
data = pd.read_csv(path)
# Drop unnecessary columns
data.drop(columns=["publisher", "dataset", "references"], inplace=True)

# Modify 'refArea' by extracting the last part after the last slash
data['refArea'] = data['refArea'].apply(lambda x: x.split('/')[-1])

# Create a sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Bar Chart", "Pie Chart", "Heat Map", "Histogram", "Initiatives", "Scatter Plot", "Filtered Map", "Tourist Spots",  "Feedback"])

# Function to display bar chart
def display_bar_chart():
    st.header("Existence of Cafes, Restaurants, and Hotels")

    # Dropdown menu for selecting category
    category = st.selectbox(
        'Select a category to view',
        ['Existence of cafes - does not exist', 'Existence of restaurants - does not exist', 'Existence of hotels - does not exist']
    )

    # Count occurrences for the selected category
    category_count = data[category].value_counts().reset_index()
    category_count.columns = ['Existence Status', 'Count']

    # Create a bar plot using Plotly Express
    fig = px.bar(category_count, x='Existence Status', y='Count', text='Count',
                 labels={'Existence Status': 'Existence Status', 'Count': 'Count'},
                 title=f'Existence of {category.split(" - ")[0]}')

    # Update the x-axis labels
    fig.update_xaxes(ticktext=['Does Not Exist', 'Exist'], tickvals=[0, 1])

    st.plotly_chart(fig)

    # Add a button to show the explanation for the bar chart
    if st.button("Show Bar Chart Explanation"):
      st.write("Explanation: We can see here that most of the Lebanese cities and villages have hotels (around 70%) "
             "but only some have restaurants or cafes (around 45%).")

# Function to display pie chart
def display_pie_chart():
    st.header("Total Number of Restaurants by Area")
    total_restaurants_by_area = data.groupby('refArea')['Total number of restaurants'].sum().reset_index()

    # Create a pie chart for total restaurants by area
    fig = px.pie(total_restaurants_by_area, names='refArea', values='Total number of restaurants',
                 title='Total Number of Restaurants by Area')

    st.plotly_chart(fig)

    if st.button("Show Pie Chart Explanation"):
      st.write("Explanation: As shown in this pie chart, the Baabda district accounts for 11% of the total number of restaurants across all districts.")

# Function to display heat map
def display_heat_map():
    st.header("Heat Map of Percentage of Total Numbers of Restaurants, Hotels, and Cafes")
    aggregated_data = data.groupby('refArea')[['Total number of restaurants', 'Total number of hotels', 'Total number of cafes']].sum().reset_index()

    # Calculate total numbers
    total_numbers = aggregated_data[['Total number of restaurants', 'Total number of hotels', 'Total number of cafes']].sum()

    # Calculate percentage data
    percentage_data = aggregated_data.copy()
    percentage_data[['Total number of restaurants', 'Total number of hotels', 'Total number of cafes']] = (
        percentage_data[['Total number of restaurants', 'Total number of hotels', 'Total number of cafes']].div(total_numbers) * 100
    )

    # Create a heat map using Plotly Express
    fig = px.imshow(
        percentage_data.set_index('refArea').T,
        labels=dict(x='Area', y='Metric', color='Percentage (%)'),
        title='Heat Map of Percentage of Total Numbers of Restaurants, Hotels, and Cafes'
    )

    st.plotly_chart(fig)

    if st.button("Show Heat Map Explanation"):
      st.write("Explanation: The heatmap reveals interesting patterns across different districts. Baabda District stands out with a higher concentration of both restaurants and cafes. Akkar Governorate has the highest percentage of cafes compared to other regions. Meanwhile, the Mount Lebanon Governorate displays a balanced distribution of restaurants, hotels, and cafes, indicating a well-rounded offering in both dining and accommodation. ")

# Function to display histogram
def display_histogram():
    st.header("Histogram of Existence of Initiatives and Projects")
    hist_data = data['Existence of initiatives and projects in the past five years to improve the tourism sector - exists'].value_counts().reset_index()
    hist_data.columns = ['Existence of Initiatives', 'Count']

    # Create a bar plot using Plotly Express
    fig = px.bar(hist_data, x='Existence of Initiatives', y='Count', text='Count',
                 labels={'Existence of Initiatives': 'Existence of Initiatives/Projects', 'Count': 'Number of Areas'},
                 title='Existence of Initiatives and Projects in the Last Five Years')

    st.plotly_chart(fig)

    if st.button("Show Histogram Explanation"):
      st.write("Explanation: As shown in this histogram, most of the cities do not have initiatives and projects to improve the tourism sector, around 88%.")

# Function to display initiatives
def display_initiatives():
    st.header("Tourism Initiatives in Lebanon")
    
    initiative_data = data['Existence of initiatives and projects in the past five years to improve the tourism sector - exists'].value_counts()
    
    # Display the bar chart
    fig = px.bar(initiative_data, x=initiative_data.index, y=initiative_data.values, 
                 labels={'x': 'Existence of Initiatives', 'y': 'Number of Areas'},
                 title='Existence of Initiatives and Projects in the Past Five Years')
    
    st.plotly_chart(fig)

    if st.button("Show Bar Plot Explanation"):
      st.write("Explanation: As shown in this bar plot, Byblos district has the highest number of initiatives with 10, followed by Mount Lebanon Governorate and Baalbek-Hermel Governorate with 9.")

# Function to display scatter plot
def display_scatter_plot():
    st.header("Total Number of Establishments per Area (Summed)")
    df = pd.DataFrame(data)
    df_grouped = df.groupby('refArea').sum().reset_index()
    df_grouped['Total'] = df_grouped['Total number of restaurants'] + df_grouped['Total number of hotels'] + df_grouped['Total number of cafes']

    # Create a scatter plot using Plotly Express
    fig = px.scatter(df_grouped, 
                     x='refArea', 
                     y='Total', 
                     size='Total',  
                     color='Total',  
                     hover_name='refArea',  
                     text='refArea',  
                     title='Total Number of Restaurants, Hotels, and Cafes per Area (Summed)',
                     labels={'Total':'Total Number of Establishments', 'refArea': 'Area'},
                     color_continuous_scale=px.colors.sequential.Plasma)

    fig.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='white')))
    fig.update_layout(
        width=1200,
        height=800,
        paper_bgcolor='#2e2e2e',
        plot_bgcolor='#2e2e2e',
        title_font=dict(size=24, family='Arial Black', color='white'),
        xaxis_title_font=dict(size=18, family='Arial', color='white'),
        yaxis_title_font=dict(size=18, family='Arial', color='white'),
        legend_title_font=dict(size=16, color='white'),
        margin=dict(l=50, r=50, t=70, b=50),
        xaxis=dict(showgrid=False, showline=True, showticklabels=True, ticks='outside'),
        yaxis=dict(showgrid=False, showline=True, showticklabels=True, ticks='outside')
    )

    st.plotly_chart(fig)

    if st.button("Show Scatter Plot Explanation"):
        st.write("Explanation: This scatter plot shows the total number of establishments in each area. Larger circles represent areas with more restaurants, hotels, and cafes combined.")

# Define coordinates for different areas
coordinates = {
    'Akkar_Governorate': (34.5078, 36.1534),
    'Mount_Lebanon_Governorate': (33.9634, 35.8347),
    'Matn_District': (34.0280, 35.8351),
    'Byblos_District': (34.1202, 35.6800),
    'Baalbek-Hermel_Governorate': (33.9061, 36.1478),
    'Aley_District': (33.8321, 35.8329),
    'Keserwan_District': (34.0376, 35.6163),
    'Tyre_District': (33.1615, 35.1146),
    'South_Governorate': (33.2721, 35.2033),
    'Sidon_District': (33.6020, 35.6924),
    'Baabda_District': (33.8750, 35.4778),
    'Miniyeh–Danniyeh_District': (34.2755, 35.7016),
    'North_Governorate': (34.4186, 35.7857),
    'Zgharta_District': (34.1564, 35.7830),
    'Nabatieh_Governorate': (33.3641, 35.6466),
    'Bint_Jbeil_District': (33.3638, 35.7387),
    'Batroun_District': (34.1755, 35.7016),
    'Zahlé_District': (33.5422, 35.8101),
    'Western_Beqaa_District': (34.2304, 35.8682),
    'Marjeyoun_District': (33.7500, 35.6924),
    'Beqaa_Governorate': (34.0868, 35.9783),
    'Bsharri_District': (34.2507, 36.0117),
    'Hasbaya_District': (33.3979, 35.6851),
    'Hermel_District': (34.3989, 36.3904),
    'Tripoli_District,_Lebanon': (34.3284, 35.9783)
}

# Ensure 'data' is defined and contains the necessary columns
# Example loading data (replace with actual data loading code):
# data = pd.read_csv('your_data_file.csv')

# Calculate total establishments
data['Total'] = (
    data['Total number of restaurants'].fillna(0) + 
    data['Total number of hotels'].fillna(0) + 
    data['Total number of cafes'].fillna(0)
)

# Aggregate data by area
aggregated_data = data.groupby('refArea').agg({'Total': 'sum'}).reset_index()
aggregated_data['Latitude'] = aggregated_data['refArea'].map(lambda x: coordinates.get(x, (None, None))[0])
aggregated_data['Longitude'] = aggregated_data['refArea'].map(lambda x: coordinates.get(x, (None, None))[1])

# Create map with default view
def display_filtered_map():
    map_center = [33.8547, 35.8623]
    m_filtered = folium.Map(location=map_center, zoom_start=8)

    def color_producer(total):
        if total < 50:
            return 'green'
        elif total < 100:
            return 'yellow'
        elif total < 200:
            return 'orange'
        else:
            return 'red'

    st.write("### Filtered Map of Tourist Establishments")

    # Add filter for the minimum total number of establishments
    min_total = st.slider('Minimum Total Number of Establishments', min_value=0, max_value=int(aggregated_data['Total'].max()), value=0)

    filtered_data = aggregated_data[aggregated_data['Total'] >= min_total]

    for i, row in filtered_data.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=10,
                popup=f"{row['refArea']}: {row['Total']}",
                color=color_producer(row['Total']),
                fill=True,
                fill_color=color_producer(row['Total']),
                fill_opacity=0.6
            ).add_to(m_filtered)

    st.subheader("Filtered Map")
    folium_static(m_filtered, width=700, height=500)

    # Add explanation button
    if st.button("Show Map Explanation"):
        st.write("Explanation: This interactive map displays the total number of tourist establishments (restaurants, hotels, and cafes) across various areas. The colors of the markers indicate the range of the total number of establishments. You can use the slider to filter areas based on the minimum number of establishments.")



# Email validation function
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

# Check if email is already in the file
def check_existing_email(email):
    if os.path.exists('submitted_emails.txt'):
        with open('submitted_emails.txt', 'r') as file:
            for line in file:
                try:
                    # Attempt to split the line by the colon separator
                    saved_email, saved_feedback = line.strip().split(':')
                    if saved_email == email:
                        return True, saved_feedback
                except ValueError:
                    # Skip lines that don't follow the email:feedback format
                    continue
    return False, None

# Save email and feedback to the file
def save_email_feedback(email, feedback):
    with open('submitted_emails.txt', 'a') as file:
        file.write(f"{email}:{feedback}\n")

# Function for feedback submission
def display_feedback_form():
    st.header("Feedback Form")

    # Get user's email
    email = st.text_input("Enter your email:")
    feedback = st.text_area("Write your feedback:")

    if st.button("Submit Feedback"):
        # Validate email format
        if not validate_email(email):
            st.error("Invalid email format. Please enter a valid email.")
        else:
            # Check if email already exists
            exists, existing_feedback = check_existing_email(email)
            if exists:
                st.warning("You have already submitted feedback.")
                st.write(f"Your previous feedback: {existing_feedback}")
            else:
                # Save email and feedback
                save_email_feedback(email, feedback)
                st.success("Thank you for your feedback!")

# Function to display insights and tourist recommendations
def display_tourist_spots():
    st.header("Tourist Spots and Insights")

    # Dropdown menu for selecting a district
    selected_district = st.selectbox('Select a district to view tourist spots and insights', options=aggregated_data['refArea'].unique())

    if selected_district:
        # Filter data for the selected district
        district_data = aggregated_data[aggregated_data['refArea'] == selected_district]
        
        if not district_data.empty:
            latitude, longitude = district_data.iloc[0]['Latitude'], district_data.iloc[0]['Longitude']
            
            # Show insights about the district
            st.write(f"### Insights for {selected_district}")
            st.write(f"- **Total Number of Establishments:** {district_data.iloc[0]['Total']}")
            
            # Create a map centered on the selected district
            map_center = [latitude, longitude]
            m_district = folium.Map(location=map_center, zoom_start=12)
            
            folium.Marker(
                location=map_center,
                popup=f"{selected_district}: {district_data.iloc[0]['Total']} establishments",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m_district)
            
            st.subheader("Map")
            folium_static(m_district, width=700, height=500)
            
            # Tourist recommendations (customize based on actual data or a list of recommendations)
            st.write("### Recommended Tourist Spots")
            # Example recommendations for different districts (customize these as needed)
            recommendations = {
    'Akkar_Governorate': ["Akkar Plains", "Mkaibeh Village", "Akkar Castle"],
    'Aley_District': ["Aley Souks", "Beirut River Valley", "Aley Forest"],
    'Baabda_District': ["Baabda Palace", "Chouf Cedars", "Deir el Qamar"],
    'Baalbek-Hermel_Governorate': ["Baalbek Ruins", "Zahle", "Qasr el Heri"],
    'Batroun_District': ["Batroun Old Town", "Roman Baths", "Batroun Beaches"],
    'Beqaa_Governorate': ["Anjar Ruins", "Baalbek Temples", "Karaoun Lake"],
    'Bint_Jbeil_District': ["Bint Jbeil Heritage", "Mleeta Resistance Museum", "Tyre Beach"],
    'Bsharri_District': ["Qadisha Valley", "Cedars of God", "Bsharri Museum"],
    'Byblos_District': ["Byblos Castle", "Old Souk", "Jeita Grotto"],
    'Hasbaya_District': ["Hasbaya Castle", "Hasbaya Souk", "Ras El Ain"],
    'Hermel_District': ["Hermel Ruins", "Lebanon River", "Mount Hermon"],
    'Keserwan_District': ["Jounieh Bay", "Harissa", "Faqra Ruins"],
    'Marjeyoun_District': ["Marjeyoun Castle", "Ajloun Nature Reserve", "The Ruins of Qasr el-Ma"],
    'Matn_District': ["Broummana", "Jdita Village", "Matn Souk"],
    'Miniyeh–Danniyeh_District': ["Miniyeh Old Town", "Danniyeh Mountains", "Saint Georges Monastery"],
    'Mount_Lebanon_Governorate': ["Jounieh Bay", "Harissa", "Faqra Ruins"],
    'Nabatieh_Governorate': ["Nabatieh Souk", "Berkayel", "Jezzine Waterfalls"],
    'North_Governorate': ["Tripoli Citadel", "Abou Ali River", "El Mina"],
    'Sidon_District': ["Sidon Sea Castle", "Ancient Sidon", "Sidon Souks"],
    'South_Governorate': ["Tyre Roman Ruins", "Jezzine Waterfalls", "Nabatieh Souk"],
    'Tripoli_District_Lebanon': ["Tripoli Citadel", "Old Tripoli", "Al-Mina Port"],
    'Tyre_District': ["Tyre Roman Ruins", "Tyre Beach", "Tyre Souks"],
    'Western_Beqaa_District': ["Baalbek Ruins", "Taanayel Lake", "Shedra"],
    'Zahlé_District': ["Zahlé River", "Zahlé Cathedral", "Wine Tours"],
    'Zgharta_District': ["Zgharta Old Town", "Mar Abda Monastery", "Qozhaya Monastery"]
}
            if selected_district in recommendations:
                for spot in recommendations[selected_district]:
                    st.write(f"- {spot}")
            else:
                st.write("No specific recommendations available for this district.")



# Display selected page
if page == "Overview":
    st.subheader("Explore Lebanon's Tourism")
    st.header("Discover Lebanon")

    # Add some images
    st.image("https://t3.ftcdn.net/jpg/03/87/74/80/360_F_387748004_MxWTt4uHfVVQ59LpqgXHMP4pomczFqQS.jpg", 
             caption="Beirut Skyline", use_column_width=True)

    st.write("""
    Lebanon's capital, Beirut, is a bustling metropolis known for its lively nightlife, historical landmarks, and beautiful Mediterranean coastline.
    """)

    st.image("https://www.new7wonders.com/app/uploads/sites/4/2016/09/16527177602_ff18053a91_o.jpg",
             caption="Jeita Grotto", use_column_width=True)

    st.write("""
    The Jeita Grotto is a stunning natural wonder, featuring impressive limestone caves and underground rivers that attract visitors from all over the world.
    """)

    st.image("http://lebanonuntravelled.com/wp/wp-content/uploads/2023/05/photo_5965516417036041360_y-1.jpg",
             caption="Byblos Old Souk", use_column_width=True)

    st.write("""
    Byblos is one of the oldest continuously inhabited cities in the world. Its ancient ruins and traditional markets are a testament to Lebanon's rich cultural heritage.
    """)
    st.write("""
- **Annual Tourist Arrivals:** Lebanon attracts millions of tourists each year, with significant contributions from countries such as Saudi Arabia, UAE, France, and the USA. The country's strategic location and historical significance make it a popular destination in the Middle East.

- **Tourism Revenue:** The tourism sector plays a crucial role in Lebanon's economy, contributing significantly to the country's GDP. The influx of international visitors supports a wide range of industries including hospitality, transportation, and local crafts.

- **Popular Attractions:**
  - **Beirut:** Known for its vibrant nightlife, cultural events, and historical landmarks. Key spots include the Corniche, the National Museum, and the iconic Pigeon Rocks.
  - **Jeita Grotto:** A natural wonder featuring impressive cave formations and subterranean rivers. It is a finalist in the New7Wonders of Nature.
  - **Byblos:** An ancient city with historical ruins and a bustling souk. The Byblos Castle and the ancient port are key attractions.
  - **Baalbek:** Famous for its Roman temples, including the Temple of Jupiter, Temple of Bacchus, and the Temple of Venus. It is a UNESCO World Heritage site.
  - **Lebanese Mountains:** Offering picturesque landscapes and outdoor activities. Popular areas include Mount Lebanon and the Cedars of God.

- **Tourist Demographics:** Visitors to Lebanon come from diverse backgrounds, with significant numbers from neighboring Arab countries as well as Western nations. The country’s historical sites, natural beauty, and cultural experiences attract a wide range of tourists.

- **Tourism Infrastructure:** Lebanon boasts a well-developed tourism infrastructure, including luxury hotels, resorts, and restaurants. The country is also known for its high-quality service and hospitality.

- **Cultural Events and Festivals:** Lebanon hosts numerous cultural events and festivals throughout the year, including music festivals, food festivals, and traditional celebrations. These events draw both local and international tourists.

- **Economic Impact:** Tourism is a major source of foreign exchange for Lebanon and provides employment opportunities across various sectors. The industry also promotes local businesses and crafts, contributing to the country's economic development.
""")
elif page == "Bar Chart":
    display_bar_chart()

elif page == "Pie Chart":
    display_pie_chart()

elif page == "Heat Map":
    display_heat_map()

elif page == "Histogram":
    display_histogram()

elif page == "Initiatives":
    display_initiatives()

elif page == "Scatter Plot":
    display_scatter_plot()

elif page == "Filtered Map":
    display_filtered_map()

elif page == "Tourist Spots":
    display_tourist_spots()

# Add feedback form
elif page == "Feedback":
    display_feedback_form()