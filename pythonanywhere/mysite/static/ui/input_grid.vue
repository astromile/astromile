<template>
    <div class="input-grid-container">
        <div :id="id">
        </div>
    </div>
</template>


<script>

import Handsontable from './handsontable.full.min.js'

export default {
	name: 'InputGrid',
	props: ['id', 'params', 'xaxis'],
	data: function(){
		return {paramColWidth:null}
	},
	mounted: function(){
		this.render_hot()
	},
	watch: {
		params: function(){
			this.render_hot()
		},
		xaxis: function() {
			this.render_hot()
		}
	},
	methods: {
		render_hot: function(){
			var data = []
			const vm = this
			
			this.params.forEach(function(p){
				data.push({
					name:p.name, 
					value:p.value, 
					xaxis:(vm.xaxis==p.id)
				})
			})
			
			const container = document.getElementById(this.id)
			container.innerHTML=''
			var settings = {
				data: data,
				colHeaders : ['Parameter','Value','X-axis'],
				rowHeaders : false,
				columns: [
					{data: 'name', readOnly:true},
					{data: 'value'},
					{data: 'xaxis', type:'checkbox'}
				],
				afterChange: function(change,source){
					//console.log('['+source+'] ' + change)
					if((source=='edit') && (change[0][1]=='value') && (change[0][2]!=change[0][3])){
						var idx = change[0][0]
						var newVal = change[0][3]
						//console.log(idx + ' :-> ' + newVal)
						vm.$emit('input',newVal, vm.params[idx].id)
					}else if((source=='edit') && (change[0][1]=='xaxis') && !change[0][2]){
						var idx = change[0][0]
						//console.log('new x-axis: ' + vm.params[idx].id)
						vm.$emit('xaxis',vm.params[idx].id)
					}else if((source=='CopyPaste.paste')){
						var newVal = {}
						change.forEach(function(ch){
							if(ch[2]!=ch[3]){
								newVal[vm.params[ch[0]].id] = ch[3]								
							}
						})
						vm.$emit('multinput',newVal)						
					}
				}
			}
			const hot = new Handsontable(container,settings)
			var colWidth = hot.getPlugin('autoColumnSize').getColumnWidth(0)
			if(this.paramColWidth != colWidth){
				this.paramColWidth = colWidth
				this.$emit('col_width_change',colWidth)
			}
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