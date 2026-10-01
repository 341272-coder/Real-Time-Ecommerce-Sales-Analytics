Real-Time E-commerce Sales Analytics
====================================

Project Overview
----------------

This project is a real-time e-commerce sales analytics system developed as part of the Streaming Data Analytics assignment. It processes simulated e-commerce orders through Apache Kafka, stores them in MongoDB Atlas, and visualizes sales performance using a Streamlit dashboard.

Business Problem
----------------

E-commerce businesses need timely information about product demand to support inventory replenishment decisions. Delayed sales reporting can contribute to stockouts, lost sales, and excess inventory.

This project demonstrates how streaming analytics can help identify fast-selling products and support more informed replenishment decisions.

System Architecture
-------------------

The system follows this workflow:

1.  **Kafka Producer:** Publishes e-commerce order records to a Kafka topic.
    
2.  **Apache Kafka:** Streams order messages through the ecommerce\_orders topic.
    
3.  **Python Consumer:** Reads messages from Kafka and stores them in MongoDB Atlas.
    
4.  **MongoDB Atlas:** Stores the order records for analysis.
    
5.  **Streamlit Dashboard:** Displays sales KPIs, charts, product performance, and inventory-related insights.
    

Technologies Used
-----------------

*   Python
    
*   Apache Kafka
    
*   Docker
    
*   MongoDB Atlas
    
*   PyMongo
    
*   Streamlit
    
*   Pandas
    
*   Plotly
    

Dataset
-------

The project uses 300 simulated e-commerce orders with unique order IDs.

The dataset includes:

*   Timestamp
    
*   Order ID
    
*   Product
    
*   Category
    
*   Quantity
    
*   Price
    
*   Total amount
    
*   Payment method
    

The data is simulated for educational and demonstration purposes and does not represent actual customer transactions.

Dashboard Features
------------------

*   Total orders and revenue KPIs
    
*   Sales trends over time
    
*   Revenue by product category
    
*   Payment method analysis
    
*   Top-selling products
    
*   Illustrative inventory replenishment insights
    
*   Automatic dashboard refresh to display incoming orders
    

Business Use Case
-----------------

The dashboard demonstrates how real-time sales information can support inventory replenishment planning by highlighting products with higher sales activity.

Inventory values are illustrative assumptions rather than actual warehouse stock data. The dashboard is a decision-support prototype and should not be treated as a production inventory management system.

Project Files
-------------

*   consumer.py – Kafka consumer and MongoDB ingestion
    
*   dashboard.py – Streamlit analytics dashboard
    
*   generate\_extra\_data.py – Generates additional simulated orders
    
*   send\_extra.py – Sends generated orders to Kafka
    
*   additional\_orders.csv – Additional simulated order data
    
*   test\_mongodb.py – MongoDB connection test
    
*   deduplicate\_orders.py – Previews duplicate order IDs
    
*   clean\_duplicates.py – Backs up the collection and removes duplicate records
    

Setup and Execution
-------------------

1.  Install Python and Docker.
    
2.  Start the Kafka container and ensure the ecommerce\_orders topic is available.
    
3.  Install the required Python packages:pip install kafka-python pymongo python-dotenv streamlit pandas plotly
    
4.  Configure the MongoDB connection string in a local .env file using the variable MONGO\_URI.
    
5.  Start the consumer:py consumer.py
    
6.  Start the dashboard in another terminal:py -m streamlit run dashboard.py
    
7.  Run the producer scripts as required to stream order data.
    

Limitations
-----------

*   The dataset is simulated.
    
*   Inventory estimates are illustrative and are not connected to a real warehouse inventory system.
    
*   The project is a prototype for demonstrating streaming analytics, not a production deployment.
    

Conclusion
----------

This project demonstrates an end-to-end streaming analytics pipeline for e-commerce sales monitoring. It combines Kafka, Python, MongoDB Atlas, and Streamlit to transform incoming order data into real-time visual insights that can support inventory-related business decisions.