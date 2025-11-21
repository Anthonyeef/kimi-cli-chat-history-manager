import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			out: 'build',
			precompress: false,
			envPrefix: ''
		}),
		alias: {
			$lib: 'src/lib',
			$components: 'src/lib/components'
		},
		// Proxy API requests to Python backend in development
		// In production, both will be served from the same domain
		paths: {
			base: ''
		}
	}
};

export default config;
