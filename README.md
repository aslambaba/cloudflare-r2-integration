## Running The Cloudflare Worker

- ### To be able to run the worker you need to have a Cloudflare account.

## Setting up the cloudflare worker

- Run the following commands to get started:

```lang=bash

    cd c3-worker
    yarn
    <!-- or  you can also  -->
    npm install

```

- Above command will install all the dependencies required to run the worker

- Go to the cloudflare dashboard under the `Workers and Pages` section create a new worker and copy the name to `c3worker/src/index.ts` file

- Go to the `wrangler.toml` file and replace the `account_id` with your cloudflare account id and `name` with the name of the worker you created in the previous step

  - On the same file replace the bucket name in the following snippet with your bucket name

  ```
   r2_buckets = [
       { binding = "MY_BUCKET", bucket_name = "<BUCKET_NAME>" , preview_bucket_name = "<BUCKET_NAME>"}
   ]

  ```

# Setting up R2 Bucket

- Go to the cloudflare dashboard under r2 section create a new bucket and copy the name.

- Next go back to `src/index.ts` and replace the `BUCKETNAME` with your bucket name. Also replace the `ACCOUNT_ID` with your account id

- Still on the Cloudflare dashboard go R2 then `Manage Api Keys` and create a new key and grant it `Admin Read and Write Permisions`.

- Next copy the `Access Key Id ` go to the `src/index.ts` and replace the `ACCESS_KEY_ID` with the key you just copied.

- Next copy the `Secret Access Key` and replace the `SECRET_ACCESS_KEY` with the key you just copied.

# Deploying the cloudflare worker

- To deploy your worker run the following commands inside your `c3-worker` folder . Rememeber to copy the `BUCKET_URL` it is going to be needed later.

```
    yarn deploy
```

# Setting up Flask Backend

- Create a new file called `.env` inside the `api` folder and add the following variables

```
    BUCKET_NAME = <BUCKET_NAME>
    ACCOUNT_ID= <ACCOUNT_ID>


    ACCESS_KEY_ID=<ACCESS_KEY_ID>

    SECRET_ACCESS_KEY=4<SECRET_ACCESS_KEY>


    REDIS_URL = <your redis url>

    WORKER_URL = <THIS  ONE WILL BE GOT AFTER DEPLOYING THE WORKER>

```

- Create an new virtual environment inside the api folder and activate it then install the requirements using the following command

```lang=bash
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

```

# Running the Flask Backend

- In your Terminal run the following commands inside the api folder

```
    export Flask_DEBUG=1
    flask run
```

- The above command will start the flask server on port 5000
# cloudflare-r2-integration
