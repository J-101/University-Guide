*Note this was originally created by me in a private repository for a school project, but then was transferred to this repository in order for it to be able to be viewed.*

**Title:**
University Guide

**Purpose:**  
This dashboard is designed to facilitate the exploration of academic data, including faculty information, publications, and university affiliations. It is aimed at academic researchers, prospective students, faculty members, administrators, and anyone interested in exploring detailed academic data from various universities and institutions. Additionally, it serves data analysts who need to interact with, search, and analyze data across multiple databases. The primary objective of this dashboard is to provide an integrated platform where users can view university details, search and edit faculty data, analyze publication information, and explore collaborations and citations, all in one place. It was made to be easy to use and understand, and provides direct comparisons to those curious.

**Installation:**
1. Clone the repo
2. Install dependencies (in requirements.txt)
3. Ensure you have three databases set up based on the AcademicWorld data (MySQL, MongoDB, & Neo4j)

**Usage:**
1. Run it using python app.py
2. Access the app by going to the link: http://127.0.0.1:8050/
3. The dashboard itself is fairly self explanatory. Can explore it and play around with the different widgets. Note that most widgets require the university to be chosen first to be used, and some require a keyword to be chosen to (as these widgets interact with one another and require data from one another). The whole process can be seen in the video demo too.

**Design:**  
This application uses a Dash-based web dashboard with Bootstrap styling. The 6 main widgets were:  
1. Select University: Allows user to select a university, then displays the basic information about the university. (MySQL database)
2. Faculty Data: Searchable and editable table for faculty members. (MongoDB database)
3. Top Collaborators: Pie chart visualizing faculty collaboration data. (Neo4j database)
4. Select Keyword: View the keywords and select a keyword from the already selected University, and use this selected keyword to display information in the next few widgets. (MySQL database)
5. Publications Data: Searchable and editable table for publications. (MongoDB database)
6. Top Faculty Members Citations: Bar chart showing the top faculty members' citations. (Neo4j database)

**Implementation:**  
- Dash: For creating the interactive web dashboard.  
- Dash Bootstrap Components & CSS: For styling and layout.  
- Python: Connecting all of the components together.  
- Plotly Express: For data visualizations.  
- Pandas: For data manipulation and integration.  
- PyMongo: Incorporating Python with MongoDB.  
- SQLAlchemy: Incorporating Python with MySQL.  
- MySQL: For university data management.  
- MongoDB: For storing and retrieving faculty and publications data.  
- Neo4j: For collaboration and citation analysis.  

As seen from what's stated above, the dashboard was implemented using a combination of web frameworks and database tools. The front-end was built with Dash and Python, providing interactive visualization components. The backend integrates MySQL, MongoDB, and Neo4j to handle relational, document data, and graph data. Data querying and manipulation were done through SQLAlchemy for MySQL, PyMongo for MongoDB, and Neo4j’s Python driver, enabling interactions across different data models.  

**Database Techniques:**
1. Indexing:  
In the Neo4j database, I created indexes to optimize query performance. For instance, I used indexes on the INSTITUTE and KEYWORD nodes:  
&nbsp;&nbsp;&nbsp;&nbsp;CREATE INDEX institute_name_idx FOR (n:INSTITUTE) ON (n.name);  
&nbsp;&nbsp;&nbsp;&nbsp;CREATE INDEX keyword_name_idx FOR (k:KEYWORD) ON (k.name);  
These indexes speed up queries that filter by university names or keywords. This makes the application more responsive when handling large datasets.  

3. View:  
In the MySQL database, I created a view called university_keywords_view to simplify complex joins and provide a streamlined way to access relevant data:  
&nbsp;&nbsp;&nbsp;&nbsp;CREATE VIEW university_keywords_view AS  
&nbsp;&nbsp;&nbsp;&nbsp;SELECT u.name AS university_name, k.name AS keyword  
&nbsp;&nbsp;&nbsp;&nbsp;FROM university u  
&nbsp;&nbsp;&nbsp;&nbsp;JOIN faculty f ON u.id = f.university_id  
&nbsp;&nbsp;&nbsp;&nbsp;JOIN faculty_keyword fk ON f.id = fk.faculty_id  
&nbsp;&nbsp;&nbsp;&nbsp;JOIN keyword k ON fk.keyword_id = k.id;  
This view allows me to easily retrieve the keywords associated with each university without needing to write out the complex joins in the code. It simplifies querying and further ensures consistency in the data accessed by the application.  

4. Prepared Statements:  
To prevent SQL injection and improve query performance, I used this prepared statements in the application when interacting with the MySQL database.  
&nbsp;&nbsp;&nbsp;&nbsp;if selected_university:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;query = f"""  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SELECT DISTINCT keyword   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FROM university_keywords_view  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WHERE university_name = %s  
&nbsp;&nbsp;&nbsp;&nbsp;"""  
&nbsp;&nbsp;&nbsp;&nbsp;df_keywords = sql_db_data(query, (selected_university,))  
The '%s' acts as a placeholder, with the actual value passed securely at runtime. This can ensure that the query is safe from injection attacks. This approach also optimizes query execution as the database can reuse the prepared statement.  
