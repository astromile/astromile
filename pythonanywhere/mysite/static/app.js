import Vue from 'vue'

import OptionPricer from './option_pricer.vue'

var app = new Vue({
	el: '#app',
	template: '<option-pricer :model="model"></option-pricer>',
	components: { 'option-pricer': OptionPricer },
	data() {
		return {
			model: model
		}
	}
})