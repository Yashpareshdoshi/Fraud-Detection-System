# Fraud-Detection-System
An advanced real-time transaction fraud detection system that simulates modern banking security architecture.
The system combines Machine Learning with rule-based risk evaluation to analyze transaction behavior, validate security constraints, and generate intelligent fraud decisions.

Overview

Traditional fraud detection systems rely either on static rules or standalone machine learning models. This project implements a hybrid approach that integrates ML-based fraud probability with real-world banking risk policies such as geo-velocity checks, transaction limits, and behavioral anomaly detection.

The system classifies transactions into Approved, Alert, or Blocked categories based on a dynamically calculated risk score.

Key Features
1. Hybrid Fraud Detection Engine
Combines Machine Learning prediction with rule-based banking constraints for realistic risk evaluation.

2. Machine Learning Risk Prediction
Generates a base fraud probability score using transaction-related features.

3. Geo-Location Tracking
Detects transaction origin using IP-based location mapping and extracts latitude and longitude.

4. Distance & Geo-Velocity Detection
Uses the Haversine formula to calculate distance between transactions and detects unrealistic travel speeds (impossible travel).

5. Amount-Based Risk Assessment
Applies dynamic risk weighting based on transaction amount and enforces maximum transaction limits.

6. Time-Based Behavioral Analysis
Identifies higher risk for transactions occurring during unusual hours.

7. Weighted Risk Scoring Model

Aggregates multiple risk factors including:

ML fraud probability

Transaction amount

Location variance

Travel speed

Time-of-day behavior

8. Multi-Level Decision Engine

Risk < 50 → Approved

Risk 50–79 → Alert

Risk ≥ 80 → Blocked

9. Real-Time Alert System
Automatically generates and stores alerts for suspicious transactions.

10. Transaction Logging & Audit Trail
Stores transaction details including risk score, decision, IP address, location, and timestamp for analysis and monitoring.

Tech Stack:

Backend

Python

Flask

Machine Learning

Scikit-learn

Database

SQL (Transaction & Alert Storage)

Geo Analytics

Haversine Formula

IP-based Location Tracking

Frontend

HTML

CSS

Bootstrap

Workflow

User submits transaction details.

System captures IP location.

Distance and travel speed are calculated.

ML model predicts fraud probability.

Rule-based engine calculates additional risk.

Final weighted risk score is generated.

Transaction is classified as Approved, Alert, or Blocked.

Transaction details are stored in the database.

Future Enhancements

Email/SMS notification system

Advanced deep learning models

Real-time payment gateway integration

Behavioral profiling using historical data

Analytics dashboard for fraud trends Industry (PCI DSS) Security Concepts
