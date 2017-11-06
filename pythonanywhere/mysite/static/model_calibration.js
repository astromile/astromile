import Vue from 'vue'

import ModelCalibration from './model_calibration.vue'

var app = new Vue({
	el: '#app',
	template: '<model-calibration :model="model"></model-calibration>',
	components: { 'model-calibration': ModelCalibration },
	data() {
		return {
			model: model
		}
	}
})