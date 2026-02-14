# Fraud-Detection-System
An advanced real-time transaction risk analysis and fraud detection dashboard designed to simulate modern banking security architecture. Built to model transaction behavior, validate risk constraints, and generate intelligent fraud decisions using a hybrid ML + rule-based engine.

🚀 Tech Stack

Backend: Python, Flask
Machine Learning: Scikit-learn (Fraud Probability Model)
Risk Engine: Custom Weighted Scoring System
Geo Analytics: Haversine Formula (Distance Calculation), IP-based Location Tracking
Database: SQL (Transaction Logging & Alert Storage)
Frontend: HTML, CSS, Bootstrap
Security Simulation: Multi-layer Risk Enforcement Engine

🛠 Core Features
💳 Transaction Risk Engine

Evaluates transactions using ML fraud probability combined with real-world banking constraints.

🌍 Geo-Location Intelligence

Detects transaction origin using IP tracking and calculates geographic variance.

✈️ Geo-Velocity (Impossible Travel) Detection

Validates travel speed between consecutive transactions.
Flags unrealistic travel (>900 km/h) as high risk.

📊 Weighted Risk Scoring Model

Combines:

ML Fraud Probability

Transaction Amount

Location Shift

Travel Speed

Time-of-Day Behavior

🚦 Go / Alert / Block Decision Engine

Low Risk → Approved

Medium Risk → Alert Generated

High Risk → Automatically Blocked

🌙 Behavioral Time Analysis

Identifies high-risk night transactions (10 PM – 6 AM).

🗄 Audit & Telemetry Logging

Stores:

Risk Score

Decision

IP Address

Location

Timestamp

Transaction Metadata

🔔 Real-Time Alert System

Generates fraud alerts for suspicious activities.

📈 Risk Governance Model

Structural Limits Simulated:

Maximum transaction threshold enforcement

Speed constraint validation (Geo-Velocity)

Risk cap thresholds (50 / 80 decision boundary)

This mimics real-world fintech fraud governance frameworks.

🔬 Intelligence Layer

The ML model provides base fraud probability, while the rule-based engine enhances contextual accuracy.

This hybrid approach reflects how real banking institutions perform:

Risk-based authentication

Behavioral fraud detection

Multi-layer transaction security

📚 References

Banking Risk-Based Authentication Frameworks

Anti-Money Laundering (AML) Transaction Monitoring Systems

Geo-Velocity Fraud Detection Models

Payment Card Industry (PCI DSS) Security Concepts
