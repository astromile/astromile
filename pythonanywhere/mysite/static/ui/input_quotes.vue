<template>
	<div class="input-grid-container">
		<div :id="id"
		     style="clear:left">
		</div>
		<button @click="calibrate">Calibrate</button>
	</div>
</template>


<script>

import Handsontable from './handsontable.full.min.js'

export default {
	name: 'InputQuotes',
	props: ['id'],
	data: function() {
		return {
			data: [{ pm: '+' }],
			hot: null
		}
	},
	mounted: function() {
		this.render_hot()
	},
	watch: {
		params: function() {
			this.render_hot()
		},
		xaxis: function() {
			this.render_hot()
		}
	},
	methods: {
		render_hot: function() {
			const vm = this

			const container = document.getElementById(this.id)
			container.innerHTML = ''
			var settings = {
				data: this.data,
				colHeaders: ['', '', 'Tenor', 'DF', 'Fwd', 'RR25', 'ATM', 'BF25'],
				rowHeaders: false,
				columns: [
					{ data: 'pm', readOnly: true },
					{ data: 'checked', type: 'checkbox' },
					{ data: 'tenor', type: 'dropdown', source: ['ON', '1W', '2W', '3W', '1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y'] },
					{ data: 'df' },
					{ data: 'fwd' },
					{ data: 'rr25' },
					{ data: 'atm' },
					{ data: 'bf25' }
				],
				/*afterChange: function(change,source){
					console.log('['+source+'] ' + change)
					if((source=='edit') && (change[0][1]=='value') && (change[0][2]!=change[0][3])){
					}else if((source=='edit') && (change[0][1]=='xaxis') && !change[0][2]){
					}else if((source=='CopyPaste.paste')){
					}
				},*/
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
			}
			this.hot = new Handsontable(container, settings)
		},
		calibrate() {
			console.log('calibrating...')
			var data = []
			this.data.forEach(function(d) {
				if (d.checked) {
					var smile = {}
					for (var p in d) {
						if (p != 'checked' && p != 'pm') {
							smile[p] = d[p]
						}
					}
					data.push(smile)
				}
			})
			this.$emit('calibrate', data)
		}
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