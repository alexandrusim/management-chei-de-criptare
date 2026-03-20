CREATE DATABASE IF NOT EXISTS SIproiect;
USE SIproiect;

CREATE TABLE Framework (
    framework_id INT PRIMARY KEY AUTO_INCREMENT,
    nume VARCHAR(100) NOT NULL
);

CREATE TABLE Algoritm (
    algoritm_id INT PRIMARY KEY AUTO_INCREMENT,
    nume VARCHAR(100) NOT NULL,
    tip VARCHAR(50) NOT NULL,
    dim_cheie INT NOT NULL
);

CREATE TABLE Fisier (
    fisier_id INT PRIMARY KEY AUTO_INCREMENT,
    nume VARCHAR(255) NOT NULL,
    extensie VARCHAR(10),
    dimensiune BIGINT,
    path VARCHAR(255)
);

CREATE TABLE Cheie (
    cheie_id INT PRIMARY KEY AUTO_INCREMENT,
    algoritm_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Activ',
    val_cheie VARCHAR(500),
    data_creare DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (algoritm_id) REFERENCES Algoritm(algoritm_id)
);

CREATE TABLE Performanta (
    performanta_id INT PRIMARY KEY AUTO_INCREMENT,
    fisier_id INT,
    algoritm_id INT,
    framework_id INT,
    timp FLOAT NOT NULL,
    memorie FLOAT NOT NULL,
    tip_operatiune VARCHAR(100),
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fisier_id) REFERENCES Fisier(fisier_id),
    FOREIGN KEY (algoritm_id) REFERENCES Algoritm(algoritm_id),
    FOREIGN KEY (framework_id) REFERENCES Framework(framework_id)
);

INSERT INTO Framework (nume) VALUES ('OpenSSL');
INSERT INTO Algoritm (nume, tip, dim_cheie) VALUES ('AES-256-CBC', 'Simetric', 256);