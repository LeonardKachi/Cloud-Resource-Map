# Cloud Resource Map

See every resource running across your AWS, Azure, and GCP accounts in one place.
No cloud experience required.

---

## What it does

- Lists every service running in your cloud account (EC2, Lambda, S3, VPC, Route 53, and more)
- Shows which services are costing you money and which are free
- Estimates your monthly cost per service
- Works with AWS, Azure, and GCP — connect one or all three
- Runs entirely on your own machine — your credentials never leave your computer

---

## Requirements

You need two things installed before you start:

- **Docker Desktop** — https://www.docker.com/products/docker-desktop
- **Git** — https://git-scm.com/downloads

That is it. No Python, no Node.js, no AWS CLI required.

---

## Quick start (5 minutes)

### Step 1 — Clone the repository

Open a terminal (on Windows: PowerShell or Command Prompt) and run:

```bash
git clone https://github.com/Cloud-Resource-Map/Cloud-Resource-Map.git
cd Cloud-Resource-Map
```

### Step 2 — Set up your AWS credentials

**Option A: Use the Terraform setup (recommended — creates a safe read-only user automatically)**

Install Terraform: https://developer.hashicorp.com/terraform/install

Then run:

```bash
cd iam
terraform init
terraform apply
```

Type `yes` when prompted. When it finishes, it will print two values:
- `AWS_ACCESS_KEY_ID`
- Run `terraform output -raw AWS_SECRET_ACCESS_KEY` to get the secret

Copy both values — you will need them in Step 3.

**Option B: Create credentials manually**

1. Go to https://console.aws.amazon.com/iam
2. Click **Users** → your username → **Security credentials**
3. Click **Create access key**
4. Copy the Access Key ID and Secret Access Key

### Step 3 — Add your credentials

Copy the example file:

```bash
# On Mac/Linux:
cp .env.example .env

# On Windows (PowerShell):
copy .env.example .env
```

Open `.env` in any text editor (Notepad works fine) and fill in your AWS keys:

```
AWS_ACCESS_KEY_ID=paste_your_key_here
AWS_SECRET_ACCESS_KEY=paste_your_secret_here
AWS_DEFAULT_REGION=us-east-1
```

Save the file.

### Step 4 — Start the app

```bash
docker compose up
```

The first time you run this, Docker will download the required software.
This takes 2–3 minutes. After that it starts in seconds.

### Step 5 — Open the app

Open your browser and go to:

```
http://localhost:3000
```

You should see your AWS resources loading.

---

## Connecting Azure (optional)

If you want to see your Azure resources:

1. Go to https://portal.azure.com
2. Open **Azure Active Directory** → **App registrations** → **New registration**
3. Name it `cloud-resource-map`, click **Register**
4. Copy the **Application (client) ID** → this is your `AZURE_CLIENT_ID`
5. Copy the **Directory (tenant) ID** → this is your `AZURE_TENANT_ID`
6. Click **Certificates & secrets** → **New client secret** → copy the value → this is your `AZURE_CLIENT_SECRET`
7. Go to **Subscriptions** → copy your Subscription ID → this is your `AZURE_SUBSCRIPTION_ID`
8. Go to your subscription → **Access control (IAM)** → **Add role assignment** → assign the `Reader` role to your app registration

Add all four values to your `.env` file, then restart:

```bash
docker compose restart
```

---

## Connecting GCP (optional)

If you want to see your GCP resources:

1. Go to https://console.cloud.google.com
2. Open **IAM & Admin** → **Service Accounts** → **Create Service Account**
3. Name it `cloud-resource-map`, click **Create and continue**
4. Assign the role **Viewer** → click **Done**
5. Click the service account → **Keys** → **Add Key** → **Create new key** → JSON → **Create**
6. This downloads a `.json` file — open it in a text editor
7. Copy the entire contents (the whole JSON object) into `GOOGLE_APPLICATION_CREDENTIALS_JSON` in your `.env` file
8. Also add your project ID to `GCP_PROJECT_ID`

Restart:

```bash
docker compose restart
```

---

## Stopping the app

```bash
docker compose down
```

---

## Security notes

- Your credentials are stored in the `.env` file on your own machine only
- The `.env` file is listed in `.gitignore` — it will never be committed to Git accidentally
- The IAM user created by Terraform has read-only permissions — it cannot create, modify, or delete anything in your account
- The app runs entirely locally — no data is sent to any external server

---

## Troubleshooting

**The app shows "Could not reach the backend"**
Make sure Docker Desktop is running, then run `docker compose up` again.

**I see "Not connected" for a provider**
Check that you filled in all required values in your `.env` file and restarted with `docker compose restart`.

**My AWS region is not us-east-1**
Change `AWS_DEFAULT_REGION` in your `.env` file to match your region (e.g. `eu-west-1`).

**I get a permissions error on AWS**
If you created credentials manually (Option B), make sure the IAM user has at minimum the `ReadOnlyAccess` AWS managed policy attached.

---

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE)
