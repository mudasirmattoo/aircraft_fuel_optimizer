# Airline Fuel Optimization Agent

This project is a proof-of-concept agent that analyzes a flight plan, fetches live weather data, and optimizes flight altitudes to save fuel. The entire workflow is automated and can be run locally or deployed on AWS.

---

## Core Technologies

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900?style=for-the-badge&logo=aws-lambda&logoColor=white)
![AWS Step Functions](https://img.shields.io/badge/AWS%20Step%20Functions-9146B6?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Amazon SQS](https://img.shields.io/badge/Amazon%20SQS-FF4F8B?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---

## Project Structure and Execution Modes

- The core logic is implemented inside the `tools/` directory with separate Python modules:
  - `ingestion.py` for loading flight plans and fetching weather.
  - `optimization.py` for altitude optimization.
  - `reporting.py` for generating reports.
- The orchestration for local development runs through two scripts at the top level:
  - `agent.py`: Defines the agent integrating the core tools and the Bedrock model.
  - `main.py`: Runs the agent locally using AWS Bedrock SDK to get outputs.
- For deployment on AWS:
  - Each core tool is adapted as a dedicated AWS Lambda function (`ingestion-lambda`, `optimization-lambda`, `reporting-lambda`).
  - A separate Lambda function (`mcp-weather-lambda`) implements fetching live weather data from CheckWX API.
  - The workflow is orchestrated by **AWS Step Functions**, invoking these Lambdas sequentially.
  - The workflow logic itself is declaratively defined in `statemachine.asl.json` using Amazon States Language.
  - The final fuel optimization report is sent to an **AWS SQS** queue for downstream operational use.

---

## Workflow Overview

1.  **Local Execution:**
    Run `main.py` that leverages `agent.py` to execute the ingestion, optimization, and reporting with live weather fetch using the AWS Bedrock SDK locally. This produces output and logs locally, validated with screenshots.
2.  **AWS Deployment:**
    - Deploy Lambda functions for ingestion, optimization, reporting, and MCP weather fetch to AWS.
    - Use AWS Step Functions to orchestrate these Lambdas in a state machine for the fuel optimization workflow.
    - The report generated in the workflow is sent to an AWS SQS queue for subsequent processing.

---

## How to Run Locally

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/mudasirmattoo/aircraft_fuel_optimizer.git
    cd aircraft_fuel_optimizer
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up environment variables:** Create a `.env` file containing:
    ```
    CHECKWX_API_KEY=YOUR_API_KEY_HERE
    ```
4.  **Run agent locally:**
    ```bash
    python main.py
    ```

---

## How to Deploy on AWS

Follow the manual or SAM deployment instructions below:

### Manual Deployment

- Package each Lambda (`ingestion-lambda`, `optimization-lambda`, `reporting-lambda`, `mcp-weather-lambda`) as a `.zip` with dependencies.
- Create an IAM role with Lambda and SQS permissions.
- Create AWS Lambda functions and upload respective zip packages.
- Deploy an SQS queue for receiving reports.
- Set environment variables as needed.
- Create an AWS Step Functions state machine by pasting the content from `statemachine.asl.json` and updating the Lambda ARNs.
- Start executions from the Step Functions console with input JSON:
  ```json
  {
    "flight_id": "FL123",
    "icao": "KJFK"
  }
  ```

## Demo Screenshots

Local Strands Agent screenshot:
<img width="1716" height="951" alt="cli output" src="https://github.com/user-attachments/assets/190d29c5-a4ac-4dde-8fff-922ef9c410c6" />

Here is a screenshot of a successful workflow execution in AWS Step Functions:

<img width="1848" height="880" alt="image" src="https://github.com/user-attachments/assets/1930d4ab-cb4f-47b8-88f3-3aca1a0bec37" />

<img width="1837" height="693" alt="image" src="https://github.com/user-attachments/assets/9de1a4d7-47a4-498c-891c-4df2f3cc7010" />

Here is the final recommendation message in the AWS SQS queue:

<img width="1870" height="918" alt="image" src="https://github.com/user-attachments/assets/2718491f-5394-488f-bf16-12727b3fdecb" />


---


Feel free to reach out for any questions or support for extending the project!
