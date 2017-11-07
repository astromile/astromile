<template>
	<div class="heston-grid-container">
		<div :id="id"
		     style="clear:left">
		</div>
	</div>
</template>


<script>

import Handsontable from './handsontable.full.min.js'

export default {
	name: 'HestonParameters',
	props: ['id', 'optParams'],
	data: function() {
		return {
			data: [
				{ id: 'var0', fixed: false, name: 'Variance', iniValue: 0.01, value: this.optParams.var0 },
				{ id: 'kappa', fixed: false, name: 'MeanRev Speed', iniValue: 1.0, value: this.optParams.kappa },
				{ id: 'theta', fixed: false, name: 'Mean Var', iniValue: 0.01, value: this.optParams.theta },
				{ id: 'xi', fixed: false, name: 'Vol of Var', iniValue: 1.0, value: this.optParams.xi },
				{ id: 'rho', fixed: false, name: 'Correlation', iniValue: 0.0, value: this.optParams.rho },
			],
			hot: null
		}
	},
	mounted: function() {
		this.render_hot()
	},
	watch: {
		optParams: function() {
			const vm = this
			this.data.forEach(function(p) {
				p.value = vm.optParams[p.id]
			})
			this.hot.render()
		}
	},
	methods: {
		render_hot: function() {
			const vm = this

			const container = document.getElementById(this.id)
			container.innerHTML = ''
			var settings = {
				data: this.data,
				colHeaders: ['Fixed', 'Param', 'Ini Value', 'Opt Value'],
				rowHeaders: false,
				columns: [
					{ data: 'fixed', type: 'checkbox' },
					{ data: 'name' },
					{ data: 'iniValue', type: 'numeric', format: '0.000000' },
					{ data: 'value', type: 'numeric', format: '0.000000', readOnly: true },
				],
				afterChange: function(change, source) {
					console.log('[' + source + '] ' + change)
					if ((source == 'edit') && (change[0][1] == 'iniValue') && (change[0][2] != change[0][3])) {
					} else if ((source == 'edit') && (change[0][1] == 'fixed')) {
						if (change[0][3]) {
							vm.data[change[0][0]].value = vm.data[change[0][0]].iniValue
						} else {
							vm.data[change[0][0]].value = ''
						}
						vm.hot.render()
					} else if ((source == 'CopyPaste.paste')) {
					}
				},
				/*
		afterOnCellMouseDown: function(e, loc) {
			console.log('onCellMouseDown: ' + loc.row + ', ' + loc.col)
			if (loc.col == 0) {
				if (vm.data[loc.row].pm == '+') {
					vm.data[loc.row].pm = '-'
					vm.data[loc.row].checked = true
					vm.data.push({ pm: '+' })
					vm.hot.render()
				} else if (vm.data[loc.row].pm == '-') {
					vm.data.splice(loc.row, 1)
					vm.hot.render()
				}
			}
		},
					*/
			}
			this.hot = new Handsontable(container, settings)
		},
	}
}
</script>

<style>
* {
	margin: 0;
	padding: 0;
}

@import './handsontable.full.min.css'
</style>