# Next Best Offer (NBO) Engine

A synthetic digital banking NBO prototype.

## Objective

Determine which banking product or marketing offer
is most relevant for each customer.

## Architecture

Customer 360
↓
Eligibility
↓
Propensity
↓
Value & Risk
↓
Arbitration
↓
Exploration / Holdout
↓
Top 1–3 Offers

## Data

This project uses entirely synthetic banking data.

No real customer or bank data is included.

## Technology

Python
SQLite
SQL
scikit-learn
pandas
NumPy
matplotlib

## Setup

python data_generation/create_database.py

python data_generation/generate_mock_data.py
