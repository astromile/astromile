<template>
	<div class="option-pricer">
		<div class="result-list">
			<input-grid id="model_input" 
    				:params="params()"
    				:xaxis="xaxis"
    				@col_width_change="onColWidthChange" 
    				@input="onParameterChange"
					@xaxis="onXAxisChange"
					@multinput="onMultiParameterChange"></input-grid>
		</div>
		
		<div class="result-list">
    		<result-item :wlabel="wlabel" label="Call:" :wvalue="wvalue" :value="pv_call" :computed="pv_computed" ></result-item>
    		<result-item :wlabel="wlabel" label="Put:" :wvalue="wvalue" :value="pv_put" :computed="pv_computed"></result-item>
		</div>
		<div class="result-list">
			<mpld3-plot id="pv_plot" :data="plot_data" :plotting="plotting"></mpld3-plot>
		</div>
	</div>
</template>

<script>

import './server.js'
import ResultItem from './ui/result_item.vue'
import InputGrid from './ui/input_grid.vue'
import Mpld3Plot from './ui/mpld3_plot.vue'

export default {
	name: 'OptionPricer',
	props: ['model'],
	data: function(){
		return {
			isBS: this.model=="Black-Scholes",
			isHeston: this.model=="Heston",

			spot: 1.6235,
			ir: 2.,
			dy: 0.,

			vol: 10.,

			var0: 0.01,
			kappa: 1.,
			theta: 0.01,
			xi: 0.5,
			rho:-0.5,

			strike: 1.6240,
			ttm: 1.,

			pv_computed: false,
			pv_call: 0,
			pv_put: 0,

			wlabel:"10rem",
			wvalue:"10rem",
			
			xaxis:'spot',
			plotting: true,
			plot_data: null
		}
	},
	computed: {
		nameMap: function(){return {
				spot: 'Spot',
				ir: 'Interest Rate',
				dy: 'Dividend Yield',
				strike: 'Strike',
				ttm: 'Maturity',
				vol: 'Volatility',
				var0: 'Variance',
				kappa: 'Mean-rev. Speed',
				theta: 'Long-term Var',
				xi: 'Vol of Var',
				rho: 'Correlation'
		}},
		modelParams: function(){
			var params = ['spot','ir','dy']
			
			if(this.isBS){
				params.push('vol')
			}else if(this.isHeston){
				params.push('var0')
				params.push('kappa')
				params.push('theta')
				params.push('xi')
				params.push('rho')				
			}
			
			params.push('strike')
			params.push('ttm')
			
			return params
		}
	},	
	methods: {
		params: function(){
			var nmap = this.nameMap
			var params = []
			var vm = this 
			this.modelParams.forEach(function(p){
				params.push({
					id:p,
					name:nmap[p],
					value:vm[p]
				})
			})
			return params
		},
		onMultiParameterChange: function(newVals) {
			for(var p in newVals) {
				if(p in this){
					this[p] = newVals[p]
				}
			}
			this.sendPriceRequest()
			this.sendPlotRequest()
		},
		onParameterChange: function(v,pname) {
			console.log(pname + ' changed to ' + v)
	    	if(pname in this){
	    		this[pname] = v
	    	}
	      this.sendPriceRequest()
	    },
	    onXAxisChange: function(xaxis) {
	    	if(xaxis!=this.xaxis){
	    		this.xaxis=xaxis
	    		this.sendPlotRequest()
	    	}
	    },
	    onColWidthChange: function(w) {
	    	this.wlabel=w + 'px'
	    	console.log(this.wlabel)
	    },
	    sendPlotRequest: function() {
	    	this.plotting = true
	    	var params = {
	        		// common params
		            spot: this.spot,
		            ir: parseFloat(this.ir)/100.,
		            dy: parseFloat(this.dy)/100.,
		            ttm: this.ttm,
		            strike: this.strike,
		            	// BS params
		            vol: parseFloat(this.vol)/100.,
		            	// Heston params
		            var0: this.var0,
	                kappa: this.kappa,
	                theta: this.theta,
	                xi: this.xi,
	                rho: this.rho,
	                
	                xaxis: this.xaxis
	    	}
	    	const vm = this
	    	sendRequest((this.model=="Heston" ? 'heston' : 'bs') + '/plot_data',params,function(res){
	    		vm.plotting = false
	    		if(res.hasOwnProperty('error')){
	    			console.log(res.error)
	    		}else{
	    			vm.plot_data = res.mpld3_data
	    		}
	    	})
	    },
	    sendPriceRequest: function(){
	    	this.pv_computed = false
	        var params = {
	        		// common params
	            spot: this.spot,
	            ir: parseFloat(this.ir)/100.,
	            dy: parseFloat(this.dy)/100.,
	            ttm: this.ttm,
	            strike: this.strike,
	            	// BS params
	            vol: parseFloat(this.vol)/100.,
	            	// Heston params
	            var0: this.var0,
                kappa: this.kappa,
                theta: this.theta,
                xi: this.xi,
                rho: this.rho
	        }
	        const vm = this
	        sendRequest((this.model=='Heston' ? 'heston' : 'bs')+'/price_anal',params,function(res){
	            vm.pv_computed = true
	            if(res.hasOwnProperty('error')){
	                vm.pv_call = res.error
	                vm.pv_put = res.error
	            }else{
		            vm.pv_call = res.pv_call
		            vm.pv_put = res.pv_put
	            }
	        })
	    }
	},
	mounted: function(){
	    this.sendPriceRequest()
	    this.sendPlotRequest()
	},
	components: {
		//'entry': Entry,
		'result-item': ResultItem,
		'input-grid': InputGrid,
		'mpld3-plot': Mpld3Plot
	}
}

</script>

<style>
	.entry-list {
		float: left;
		margin-top: 5px;
		margin-bottom: 5px;
	}

    .result-list{
		float: left;
		clear: left;
        margin-top: 2rem;
    }
</style>