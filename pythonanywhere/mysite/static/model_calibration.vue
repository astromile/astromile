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
					<input-quotes id="input_data"
					              ref="vueInputQuote"></input-quotes>
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
				<dropdown id="objective"
				          label="Fit"
				          v-model="objective"
				          :items="['PV','Vols']"
				          :wlabel="wlabel"
				          :wvalue="wvalue"></dropdown>
				<div class="heston-params">
					<heston-params id="heston_params"
					               :optParams="heston_params"
					               ref="hparams"></heston-params>
				</div>
				<button @click="calibrate"
				        :width="wlabel">Calibrate</button>
			</div>
		</collapsable>
		<collapsable label="Plot">
			<div class="plot">
				<dropdown id='yaxis'
					label='Y-axis'
					v-model="yaxis"
					:items="['Volatility','Total Var.', 'PV','Density']"
					:wlabel="wlabel"
					:wvalue="wvalue"
					:disabled="plotting"></dropdown>
				<mpld3-plot id="fit_plot"
				            :data="plot_data"
				            :plotting="plotting"></mpld3-plot>
				<dropdown id='xaxis'
					label='X-axis'
					v-model="xaxis"
					:items="['Strike', 'Log-Moneyness', 'Delta']"
					:wlabel="wlabel"
					:wvalue="wvalue"
					:disabled="plotting"></dropdown>
			</div>
		</collapsable>
	</div>
</template>

<script>
import "./server.js";

import Entry from "./ui/entry.vue";
import Dropdown from "./ui/dropdown.vue";
import Collapsable from "./ui/collapsable.vue";

import Mpld3Plot from "./ui/mpld3_plot.vue";
import InputQuotes from "./ui/input_quotes.vue";
import HestonParams from "./ui/heston_params.vue";

export default {
  name: "ModelCalibration",
  props: ["model"],
  data: function() {
    return {
      wlabel: "5rem",
      wvalue: "5rem",

      spot: 1.6235,
      ir: 2,
      dy: 0,

      vol: 10,

      var0: 0.01,
      kappa: 1,
      theta: 0.01,
      xi: 0.5,
      rho: -0.5,

      strike: 1.624,
      ttm: 1,

      pv_computed: false,
      pv_call: 0,
      pv_put: 0,

      wlabel: "10rem",
      wvalue: "10rem",

      xaxis: "spot",
      plotting: true,
      plot_data: null,
      objective: "PV",
      method: "Nelder-Mead",
      methods: ["Nelder-Mead", "Powell", "Cobyla", "MC"],

      yaxis: "Volatility",
      xaxis: "Strike",

      premiumType: "Excluded",

      heston_params: { var0: "", kappa: "", theta: "", xi: "", rho: "" }
    };
  },
  methods: {
    calibrate: function() {
      this.plotting = true;
      const vm = this;
      var iniParams = {};
      this.$refs.hparams.data.forEach(function(p) {
        iniParams[p.id] = { value: p.iniValue, fixed: p.fixed };
      });
      //console.log(this.$refs.hparams.data)
      var params = {
        spot: this.spot,
        input_quotes: JSON.stringify(
          this.$refs.vueInputQuote.getSelectedQuotes()
        ),
        ini_params: JSON.stringify(iniParams),
        premium_type: this.premiumType,
        objective: this.objective,
        method: this.method
      };
      console.log("sending calibration request...");

      sendRequest("heston/calibrate", params, function(res) {
        if (res.hasOwnProperty("error")) {
          console.log("...calibration finished with error:");
          console.log(res.error);
          vm.plotting = false;
        } else {
          console.log(
            "...calibration finished in " +
              res.elapsedCalibration +
              " (out off total " +
              res.elapsedTime +
              ")"
          );
          vm.heston_params = res.hestonParams;
          vm.objective_value = res.objectiveValue;
          vm.plotCalibratedCurves();
        }
      });
    },
    plotCalibratedCurves(e) {
      this.plotting = true;
      var pparams = {
        spot: this.spot,
        heston_params: JSON.stringify(this.heston_params),
        input_quotes: JSON.stringify(
          this.$refs.vueInputQuote.getSelectedQuotes()
        ),
        objective_value: this.objective_value,
        premium_type: this.premiumType,
        xaxis: this.xaxis,
        yaxis: this.yaxis
      };
      const vm = this;
      sendRequest("heston/plot", pparams, function(res) {
        vm.plotting = false;
        console.log(res);
        vm.plot_data = res.plotData;
      });
    }
  },
  watch: {
    xaxis: function(newVal, oldVal) {
      if (newVal != oldVal) {
        this.plotCalibratedCurves();
      }
    },
    yaxis: function(newVal, oldVal) {
      if (newVal != oldVal) {
        this.plotCalibratedCurves();
      }
    }
  },
  mounted: function() {},
  components: {
    entry: Entry,
    dropdown: Dropdown,
    collapsable: Collapsable,
    "input-quotes": InputQuotes,
    "mpld3-plot": Mpld3Plot,
    "heston-params": HestonParams
  }
};
</script>

<style>
.entry-list > div {
  clear: left;
}

.heston-params {
  padding: 5px;
}

.market-qutes {
  padding: 5px;
}
</style>