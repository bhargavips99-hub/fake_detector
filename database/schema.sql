CREATE DATABASE IF NOT EXISTS fake_detector;

USE fake_detector;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE news_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    news_text LONGTEXT NOT NULL,
    prediction ENUM(
        'Likely Reliable',
        'Needs Verification',
        'Likely Misleading'
    ) NOT NULL,
    raw_prediction ENUM('Real', 'Fake') NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    trust_score DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);