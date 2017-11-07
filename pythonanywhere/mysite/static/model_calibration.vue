<template>
	<div>
		<div class="entry-list">
			<entry id="spot"
			       label="Spot"
			       v-model="spot"
			       wlabel="5rem"
			       wvalue="5rem"></entry>
		</div>
		<div class="heston-params">
			<heston-params id="heston_params"
			               :optParams="heston_params"
			               ref="hparams"></heston-params>
		</div>
		<div class="market-quotes">
			<input-quotes id="input_data"
			              @calibrate="calibrate"></input-quotes>
		</div>
		<div class="plot">
			<mpld3-plot id="fit_plot"
			            :data="plot_data"
			            :plotting="plotting"></mpld3-plot>
		</div>
	</div>
</template>

<script>

import './server.js'
import InputQuotes from './ui/input_quotes.vue'
import Entry from './ui/entry.vue'
import Mpld3Plot from './ui/mpld3_plot.vue'
import HestonParams from './ui/heston_params.vue'

export default {
	name: 'ModelCalibration',
	props: ['model'],
	data: function() {
		return {
			spot: 1.6235,
			ir: 2.,
			dy: 0.,

			vol: 10.,

			var0: 0.01,
			kappa: 1.,
			theta: 0.01,
			xi: 0.5,
			rho: -0.5,

			strike: 1.6240,
			ttm: 1.,

			pv_computed: false,
			pv_call: 0,
			pv_put: 0,

			wlabel: "10rem",
			wvalue: "10rem",

			xaxis: 'spot',
			plotting: true,
			plot_data: null,

			heston_params: { var0: '', kappa: '', theta: '', xi: '', rho: '' },
		}
	},
	methods: {
		calibrate: function(data) {
			this.plotting = true
			const vm = this
			var iniParams = {}
			this.$refs.hparams.data.forEach(function(p) {
				iniParams[p.id] = { value: p.iniValue, fixed: p.fixed }
			})
			console.log(this.$refs.hparams.data)
			var params = {
				spot: this.spot,
				input_quotes: JSON.stringify(data),
				ini_params: JSON.stringify(iniParams)
			}
			sendRequest('heston/calibrate', params, function(res) {
				console.log('...calibration finished in ' + res.elapsedTime)
				console.log(res)
				vm.plotting = false
				vm.heston_params = res.hestonParams
				vm.plot_data = res.plotData
			})
		}
	},
	mounted: function() {
	},
	components: {
		'entry': Entry,
		'input-quotes': InputQuotes,
		'mpld3-plot': Mpld3Plot,
		'heston-params': HestonParams,
	}
}

</script>

<style>
.heston-params {
	padding: 5px;
}

.market-qutes {
	padding: 5px;
}
</style>