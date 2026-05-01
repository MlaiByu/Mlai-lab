USE sqli_db;

DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    password VARCHAR(50)
);
INSERT INTO users VALUES
(1,'admin','admin123'),
(2,'guest','guest123');

DROP TABLE IF EXISTS flag;
CREATE TABLE flag(
    id INT PRIMARY KEY,
    flag VARCHAR(100)
);
INSERT INTO flag VALUES
(1,'Mlai{sqli_hard_double_write_bypass}');