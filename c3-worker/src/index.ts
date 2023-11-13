import { AwsClient } from 'aws4fetch';
import { v4 as uuid } from 'uuid';

export interface Env {
	MY_BUCKET: R2Bucket;
}

const SECRET_AUTH_KEY = 'TEST-AUTH-KEY';
const BUCKETNAME = '';
const ACCOUNT_ID = '';
const ACCESS_KEY_ID = ''; // R2 Bucket access key
const SECRET_ACCESS_KEY = '';

const r2 = new AwsClient({
	accessKeyId: ACCESS_KEY_ID,
	secretAccessKey: SECRET_ACCESS_KEY,
});

const ALLOW_LIST = ['secure-file-upload'];

// Check requests for a pre-shared secret
const hasValidHeader = (request: any, env: any) => {
	// return request.headers.get('X-Custom-Auth-Key') === env.AUTH_KEY_SECRET;
	return request.headers.get('X-Custom-Auth-Key') === SECRET_AUTH_KEY;
};

function authorizeRequest(request: any, env: any, key: any) {
	switch (request.method) {
		case 'PUT':
		case 'POST':
		case 'DELETE':
			return hasValidHeader(request, env);
		case 'GET':
			return ALLOW_LIST.includes(key);
		default:
			return false;
	}
}

async function fileExists(filename: any, env: Env) {
	console.log(env.MY_BUCKET);
	let key = await env.MY_BUCKET.get(filename);
	console.log('============> key', key);
	if (key === null) {
		return false;
	}
	return true;
}

async function generateNewFilename(filename: any, env: Env) {
	if (await fileExists(filename, env)) {
		const [name, ext] = filename.split('.');
		const random = uuid();

		return `${name}-${random}.${ext}`;
	}
	return filename;
}

async function generateSignedUrls(req: Request, r2: AwsClient, env: Env) {
	const requestPath = new URL(req.url).pathname;

	// Cannot upload to the root of a bucket
	if (requestPath === '/') {
		return new Response('Missing a filepath', { status: 400 });
	}

	const bucketName = BUCKETNAME;
	const accountId = ACCOUNT_ID;

	const url = new URL(`https://${bucketName}.${accountId}.r2.cloudflarestorage.com`);

	let filename = requestPath.slice(1);
	console.log('============> filename', filename);
	let newPath = await generateNewFilename(filename, env);

	// preserve the original path
	url.pathname = newPath;

	filename = newPath;

	// Specify a custom expiry for the presigned URL, in seconds
	url.searchParams.set('X-Amz-Expires', '3600');
	// set callback url

	const signed = await r2.sign(
		new Request(url, {
			method: 'PUT',
		}),
		{
			aws: { signQuery: true },
		}
	);

	return new Response(JSON.stringify({ filename: filename, signed_url: signed.url }), { status: 200 });
}

export default {
	async fetch(request: Request, env: Env, ctx: any) {
		const url = new URL(request.url);
		var key = url.pathname.slice(1);

		let object = await env.MY_BUCKET.get(key);
		console.log(object);

		if (object !== null) {
			// return new Response('File already exists', { status: 404 });
		}

		if (!authorizeRequest(request, env, key)) {
			return new Response('Forbidden', { status: 403 });
		} else if (request.method === 'GET') {
			return new Response('========> STATUS OK  ====> SECURE FILE  API REACHED', { status: 400 });
		}

		return generateSignedUrls(request, r2, env);
	},
};
