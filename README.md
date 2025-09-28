# Airline Fuel Optimization Agent

I built this project as a proof-of-concept for a coding challenge. It's an agent that analyzes a flight plan, fetches live weather data, and suggests altitude changes to save fuel. The entire workflow is automated and runs on AWS.



## Core Technologies

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900?style=for-the-badge&logo=aws-lambda&logoColor=white)
![AWS Step Functions](https://img.shields.io/badge/AWS%20Step%20Functions-9146B6?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Amazon SQS](https://img.shields.io/badge/Amazon%20SQS-FF4F8B?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


## How It Works

The project is an event-driven workflow orchestrated by AWS Step Functions.

1.  The workflow starts, triggering the `ingestion-lambda`.
2.  **Ingestion:** The first Lambda loads a static flight plan and then calls the **CheckWX API** to fetch live weather data for each waypoint.
3.  **Optimization:** The data is passed to the `optimization-lambda`, which runs a simple algorithm to find the altitudes with the lowest fuel burn rate.
4.  **Reporting:** The final report, containing the original plan, optimized plan, and savings, is passed to the `reporting-lambda`, which sends it as a JSON message to an AWS SQS queue.


## Demo Screenshots

Here is a screenshot of a successful workflow execution in AWS Step Functions:

<img width="1848" height="880" alt="image" src="https://github.com/user-attachments/assets/1930d4ab-cb4f-47b8-88f3-3aca1a0bec37" />

<img width="1837" height="693" alt="image" src="https://github.com/user-attachments/assets/9de1a4d7-47a4-498c-891c-4df2f3cc7010" />

Here is the final recommendation message in the AWS SQS queue:

<img width="1870" height="918" alt="image" src="https://github.com/user-attachments/assets/2718491f-5394-488f-bf16-12727b3fdecb" />


## How to Run

This project uses the **AWS Serverless Application Model (SAM)** to make setup and deployment easy. The following steps will create all the necessary AWS resources for you.

### 1. Prerequisites
* **Git**
* **Python 3.9+**
* **Docker** (must be running for SAM to build the packages)
* **AWS CLI** with credentials configured (run `aws configure`)
* **AWS SAM CLI** installed ([see installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))

### 2. Setup and Configuration
1.  **Clone the repository:**
    ```bash
    git clone (https://github.com/mudasirmattoo/aircraft_fuel_optimizer.git)
    cd aircraft_fuel_optimizer
    ```
2.  **Configure the Ingestion Lambda:** Create a `.env` file inside the `ingestion_lambda` folder with your CheckWX API key:
    ```
    # ingestion_lambda/.env
    CHECKWX_API_KEY=YOUR_API_KEY_HERE
    ```
3.  **Configure the Reporting Lambda:** Create a `.env` file inside the `reporting_lambda` folder. The SQS Queue will be created by SAM, so we'll add the URL after the first deployment. For now, create the file with a placeholder:
    ```
    # reporting_lambda/.env
    SQS_QUEUE_URL=placeholder
    ```

### 3. Build and Deploy
1.  **Build the application:** This command packages your Lambda functions with their dependencies.
    ```bash
    sam build
    ```
2.  **Deploy to AWS:** This command deploys all the resources defined in `template.yaml` to your AWS account. The `--guided` flag will prompt you for configuration the first time you run it.
    ```bash
    sam deploy --guided
    ```
    * **Stack Name:** Give it a name like `fuel-optimization-agent`.
    * **AWS Region:** Enter your preferred region (e.g., `ap-south-1`).
    * Accept the defaults for the remaining prompts.

### 4. Final Configuration
1.  After deployment, go to the **AWS CloudFormation** console, find your stack (`fuel-optimization-agent`), and go to the **Outputs** tab.
2.  Copy the `Value` for the `RecommendationsQueueUrl`.
3.  Update your `reporting_lambda/.env` file with this real URL.
4.  Run `sam build` and `sam deploy` one more time to update the Lambda with the correct queue URL.

### 5. Run the Workflow
1.  Go to the **AWS Step Functions** console.
2.  Find and click on the state machine named `FuelOptimizationStateMachine-...`.
3.  Click **Start execution**.
4.  In the input dialog, paste the following JSON and then click **Start execution** again:
    ```json
    {
      "flight_id": "FL123"
    }
    ```

You can now watch the workflow execute visually and check the SQS queue for the final message.

## Fulfilling the Assignment Requirements

* **AWS Strands**: This conceptual requirement was implemented using **AWS Step Functions**. It provides the stateful workflow orchestration needed to connect the different data processing steps.
* **MCP (Mission Control Protocol)**: This was implemented by sending the final JSON report to an **AWS SQS queue**. This simulates distributing the agent's recommendation to a separate operational system.
* **Fetch METAR/TAF reports**: This is handled in the `ingestion-lambda` by making live API calls to the **CheckWX API** for each waypoint.
