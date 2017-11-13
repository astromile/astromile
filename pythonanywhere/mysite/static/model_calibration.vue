<template>
	<div>
		<collapsable label="Market data">
			<div class="entry-list">
				<entry id="spot"
							label="Spot"
							v-model="spot"
							:wlabel="wlabel"
							:wvalue="wvalue"></entry>
				<dropdown id="premiumType"
									label="Premium Type"
									v-model="premiumType"
									:items="['Excluded','Included']"
									:wlabel="wlabel"
									:wvalue="wvalue"></dropdown>
				<div class="market-quotes">
					<input-quotes id="input_data" ref="vueInputQuote"></input-quotes>
				</div>
			</div>
		</collapsable>
		<collapsable label="Model Parameters">
			<div>
				<dropdown id="method"
									label="Method"
									v-model="method"
									:items="methods"
									:wlabel="wlabel"
									:wvalue="wvalue"></dropdown>
				<div class="heston-params">
					<heston-params id="heston_params"
												:optParams="heston_params"
												ref="hparams"></heston-params>
				</div>
				<button @click="calibrate" :width="wlabel" >Calibrate</button>
			</div>
		</collapsable>
		<collapsable label="Plot">
			<div class="plot">
				<mpld3-plot id="fit_plot"
										:data="plot_data"
										:plotting="plotting"></mpld3-plot>
			</div>
		</collapsable>
	</div>
</template>

<script>

import './server.js'

import Entry from './ui/entry.vue'
import Dropdown from './ui/dropdown.vue'
import Collapsable from './ui/collapsable.vue'

import Mpld3Plot from './ui/mpld3_plot.vue'
import InputQuotes from './ui/input_quotes.vue'
import HestonParams from './ui/heston_params.vue'


export default {
	name: 'ModelCalibration',
	props: ['model'],
	data: function() {
		return {
			wlabel:'5rem',
			wvalue:'5rem',

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
			method: 'Nelder-Mead',
			methods: ['Nelder-Mead', 'Powell', 'Cobyla', 'MC'],

			premiumType: 'Excluded',

			heston_params: { var0: '', kappa: '', theta: '', xi: '', rho: '' },
		}
	},
	methods: {
		calibrate: function() {
			this.plotting = true
			const vm = this
			var iniParams = {}
			this.$refs.hparams.data.forEach(function(p) {
				iniParams[p.id] = { value: p.iniValue, fixed: p.fixed }
			})
			//console.log(this.$refs.hparams.data)
			var params = {
				spot: this.spot,
				input_quotes: JSON.stringify(this.$refs.vueInputQuote.getSelectedQuotes()),
				ini_params: JSON.stringify(iniParams),
				method: this.method
			}
			console.log('sending calibration request...')
			sendRequest('heston/calibrate', params, function(res) {
				console.log('...calibration finished in ' + res.elapsedCalibration +' (out off total ' + res.elapsedTime+')')

				if(res.hasOwnProperty('error')){
					console.log(res.error)
				}
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
		'dropdown': Dropdown,
		'collapsable': Collapsable,
		'input-quotes': InputQuotes,
		'mpld3-plot': Mpld3Plot,
		'heston-params': HestonParams,
	}
}

</script>

<style>
.entry-list>div {
	clear: left;
}

.heston-params {
	padding: 5px;
}

.market-qutes {
	padding: 5px;
}
</style>