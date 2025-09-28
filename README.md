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


## How to Run (Recommended: AWS SAM)

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
    git clone https://github.com/mudasirmattoo/aircraft_fuel_optimizer.git
    cd aircraft_fuel_optimizer
    pip install requirements.txt
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
---

## Alternative: Manual Deployment via AWS Console

The following steps detail how to deploy all resources manually using the AWS Management Console.

### Step 1: Prepare Lambda Packages
First, prepare the `.zip` files for each Lambda function locally.

1.  **Install dependencies into each folder:**
    ```bash
    # For the ingestion lambda
    pip install pandas requests python-dotenv -t ingestion_lambda/

    # For the optimization lambda (no external dependencies needed)

    # For the reporting lambda
    pip install python-dotenv -t reporting_lambda/
    ```
2.  **Create the zip files:**
    ```bash
    # Zip the ingestion package
    cd ingestion_lambda && zip -r ../ingestion_lambda.zip . && cd ..

    # Zip the optimization package
    cd optimization_lambda && zip -r ../optimization_lambda.zip . && cd ..

    # Zip the reporting package
    cd reporting_lambda && zip -r ../reporting_lambda.zip . && cd ..
    ```

### Step 2: Create AWS Resources
1.  **Create IAM Role:**
    * Go to the **IAM Console**, navigate to **Roles**, and click **Create role**.
    * Select **AWS service** as the trusted entity and **Lambda** as the use case.
    * Attach the `AWSLambdaBasicExecutionRole` and `AmazonSQSFullAccess` policies.
    * Name the role (e.g., `FuelOptimizerLambdaRole`) and create it.

2.  **Create SQS Queue:**
    * Go to the **SQS Console**, click **Create queue**.
    * Keep the **Standard** type, give it a name (e.g., `FuelOptimizationRecommendations`), and create it.
    * Copy the **Queue URL** for a later step.

3.  **Create Lambda Functions:**
    * Go to the **Lambda Console** and create three separate functions (`ingestion-lambda`, `optimization-lambda`, `reporting-lambda`).
    * For each function:
        * Choose **Author from scratch**, select the **Python 3.9** runtime.
        * Under Permissions, choose **Use an existing role** and select the `FuelOptimizerLambdaRole` you created.
        * After creating the function, upload the corresponding `.zip` package.
        * For the `reporting-lambda`, go to **Configuration > Environment variables** and add a variable with the **Key** `SQS_QUEUE_URL` and the **Value** as the queue URL you copied.
        * **Copy the ARN** of each function after it's created.

### Step 3: Create the Step Functions State Machine
1.  Go to the **Step Functions Console** and click **Create state machine**.
2.  Choose **Write your workflow in code**.
3.  Paste the following JSON definition, replacing the placeholder ARNs with the actual ARNs of your Lambda functions:
    ```json
    {
      "Comment": "State machine to orchestrate the Airline Fuel Optimization workflow.",
      "StartAt": "IngestFlightData",
      "States": {
        "IngestFlightData": {
          "Type": "Task",
          "Resource": "PASTE_YOUR_INGESTION_LAMBDA_ARN_HERE",
          "Next": "OptimizeFuel"
        },
        "OptimizeFuel": {
          "Type": "Task",
          "Resource": "PASTE_YOUR_OPTIMIZATION_LAMBDA_ARN_HERE",
          "Next": "DistributeReport"
        },
        "DistributeReport": {
          "Type": "Task",
          "Resource": "PASTE_YOUR_REPORTING_LAMBDA_ARN_HERE",
          "End": true
        }
      }
    }
    ```
4.  Give the state machine a name and create it.

### Step 4: Run the Workflow
1.  Go to your newly created state machine and click **Start execution**.
2.  Provide the input JSON:
    ```json
    {
      "flight_id": "FL123"
    }
    ```
3.  Click **Start execution** and observe the visual workflow.

## Fulfilling the Assignment Requirements

* **AWS Strands**: This conceptual requirement was implemented using **AWS Step Functions**. It provides the stateful workflow orchestration needed to connect the different data processing steps.
* **MCP (Mission Control Protocol)**: This was implemented by sending the final JSON report to an **AWS SQS queue**. This simulates distributing the agent's recommendation to a separate operational system.
* **Fetch METAR/TAF reports**: This is handled in the `ingestion-lambda` by making live API calls to the **CheckWX API** for each waypoint.
