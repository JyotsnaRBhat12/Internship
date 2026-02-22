CREATE DATABASE IF NOT EXISTS student_db;
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    grade VARCHAR(10),
    email VARCHAR(100)
);


+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| id    | int          | NO   | PRI | NULL    | auto_increment |
| name  | varchar(100) | NO   |     | NULL    |                |
| age   | int          | YES  |     | NULL    |                |
| grade | varchar(10)  | YES  |     | NULL    |                |
| email | varchar(100) | YES  |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
