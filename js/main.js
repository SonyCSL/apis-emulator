

var ids = [];
var debug=false;

var form, id;

var url_emu, url_dcdc;
var param_emu, param_dcdc;

var mode;

$(document).ready(function () {
	$("form").each(function() {
	   ids.push(this.id);   
	});
	$.getJSON("./get/log", function (json) {
		updateAllUnitForm(json);
	});
	$.getJSON("./get/acc", function (json) {
		$("#acc").val(json);
	});
	
	setInterval(function(){
		if ($('#auto_refresh').is(':checked')) {
			$.getJSON("./get/log", function (json) {
				updateAllUnitForm(json);
			});
		}
	}, 5000);
})



$(function () {
	$(".read").click(function () {
		form = $(this).parents('form');
		id = $(form).attr('id');
		getAll(id, true, true);
	});

	$(".set").click(function () {
		form = $(this).parents('form');
		id = $(form).attr('id');
		setAll(id, true, true);
	});

	$(".read_all").click(function () {
		$.getJSON("./get/log", function (json) {
			updateAllUnitForm(json);
		});
	});

	$(".set_all").click(function () {
		$.getJSON("./get/log", function (json) {
			for (var oesid in json) {
				console.log(oesid);
				setAll(oesid, true, true);
			}
		});
	});

	$(".save_all").click(function () {
		$.getJSON("./save", function (json) {});
	});

	$(".load_last").click(function () {
		$.getJSON("./get/last", function (json) {
			location.reload();
		});
	});

	$(".reset").click(function () {
		$.getJSON("./restart", function (json) {
			location.reload();
		});
	});

	$(".add_unit").click(function () {
		$.getJSON("./add/unit", function (json) {
			location.reload();
		});
	});

	$(".remove_unit").click(function () {
		$.getJSON("./remove/unit", function (json) {
			location.reload();
		});
	});

	$(".set_acc").click(function () {
		acc = $("#acc").val();
		$.getJSON("./set/acc/"+acc, function (json) {});
	});



	function sendGet(url, id, form) {
		$.getJSON(url, function (json) {
			updateDCDC(form,id, json[id], Processing.getInstanceById('OES'));
		});
	}
});

function getAll(id, urgent, status){
	form =$('#field'+id).find("form");
	$.getJSON("./get/unit/"+id+"?urgent="+urgent, function (json) {
		if (status){
			updateEmu(form, id, json);
			updateDCDC(form, id, json);
		}
	}, "html");

/*	$.getJSON("./get/emu/"+id, function (json) {
		
	}, "html");*/
}

function setAll(id, urgent, status){
	form =$('#field'+id).find("form");

	var charge_discharge_power = $(form).find('#charge_discharge_power').val();
	var rsoc = $(form).find('#rsoc').val();
	var ups_output_power = $(form).find('#ups_output_power').val();
	var pvc_charge_power = $(form).find('#pvc_charge_power').val();
	mode = $(form).find('#status').val();

	param_emu = '?charge_discharge_power=' + charge_discharge_power + '&rsoc=' + rsoc + '&ups_output_power=' + ups_output_power + '&pvc_charge_power=' + pvc_charge_power;// + "&callback=?";
	url_emu = "./set/emu/"+id+param_emu;
		
	$.ajax({
		type: 'GET',
		url: url_emu,
		dataType: 'json',
		success: function(json){
			form =$('#field'+id).find("form");
			updateEmu(form, id, json[id]);
			var p1 = $(form).find('#p1').val();
			var p2 = $(form).find('#p2').val();
			var dig = $(form).find('#dig').val();
			var dvg = $(form).find('#dvg').val();
			var drg = $(form).find('#drg').val();
			mode = $(form).find('#status').val();
			param_dcdc = '?mode=' + mode + '&dig=' + dig + '&dvg=' + dvg+ '&p1=' + p1 + '&p2=' + p2  + '&drg=' + drg ;
			url_dcdc = "./set/dcdc/"+id+param_dcdc;
			$.getJSON(url_dcdc, function (json) {
				$.getJSON("./get/log", function (json) {
					updateAllUnitForm(json);
				});
			});
		}
	});
}

function updateDCDC(form, id, json){
	var dvg = json["dcdc"]["vdis"]["dvg"].toFixed(2);
	var drg = json["dcdc"]["vdis"]["drg"].toFixed(2);
	var dig = json["dcdc"]["param"]["dig"].toFixed(2);
	var p1 = json["dcdc"]["powermeter"]["p1"].toFixed(2);
	var p2 = json["dcdc"]["powermeter"]["p2"].toFixed(2);
	$(form).find('#dig').val(dig);
	$(form).find('#dvg').val(dvg);
	$(form).find('#drg').val(drg);
	$(form).find('#p1').val(p1);
	$(form).find('#p2').val(p2);
	updateMeter(id, json);
	updateJsonForm(form, id, json);
}

function updateMeter(id, json){
	var meterdiv = $('#field'+id).find(".meter");
	$(meterdiv).find(".vg").text(json.dcdc.meter.vg);
	$(meterdiv).find(".ig").text(json.dcdc.meter.ig);
	$(meterdiv).find(".wg").text(json.dcdc.meter.wg);
	$(meterdiv).find(".vb").text(json.dcdc.meter.vb);
	$(meterdiv).find(".ib").text(json.dcdc.meter.ib);
	$(meterdiv).find(".wb").text(json.dcdc.meter.wb);
	// BS
	$('#field'+id).find(".battery").text("Battery Status : "+json.emu.rsoc+" %");
	// OP
	var loss= json["dcdc"]["meter"]["wb"]-json["dcdc"]["meter"]["wg"];
	$('#field'+id).find(".loss").text("Operating power: "+loss.toFixed(0)+" W");
	// others
	$('#field'+id).find(".charge_discharge_power").text("Charge discharge power: "+json.emu.charge_discharge_power.toFixed(0));
	$(form).find('#charge_discharge_power').val(json.emu.charge_discharge_power.toFixed(0));
	$('#field'+id).find(".ups_output_power").text("UPS output power: "+json.emu.ups_output_power.toFixed(0));
	$('#field'+id).find(".pvc_charge_power").text("PVC charge power: "+json.emu.pvc_charge_power.toFixed(0));
	$('#field'+id).find(".p1").text("Powermeter all: "+json.dcdc.powermeter.p1.toFixed(0));
	$('#field'+id).find(".p2").text("powermeter p2: "+json.dcdc.powermeter.p2.toFixed(0));
}

function updateEmu(form, id, json){
	$('#field'+id).find(".battery").text("Battery Status : "+json.emu.rsoc+"%");
	$('#field'+id).find(".charge_discharge_power").text("Charge discharge power: "+json.emu.charge_discharge_power);
	$('#field'+id).find(".ups_output_power").text("UPS output power: "+json.emu.ups_output_power);
	$('#field'+id).find(".pvc_charge_power").text("PVC charge power: "+json.emu.pvc_charge_power);
	$(form).find('#charge_discharge_power').val(json.emu.charge_discharge_power);
	$(form).find('#rsoc').val(json.emu.rsoc);
	$(form).find('#ups_output_power').val(json.emu.ups_output_power);
	$(form).find('#pvc_charge_power').val(json.emu.pvc_charge_power);
	updateJsonForm(form, id, json);
}

function updateAllUnitForm(json){
	for (var oesid in json) {
		// JSON
		$('#'+oesid+' [name=json_txt]').empty();
		$('#'+oesid+' [name=json_txt]').append('<h2>'+oesid+'</h2><hr>');
		$('#'+oesid+' [name=json_txt]').append('<div>'+json[oesid]["oesunit"]["display"]+'</div><hr>');
		$('#'+oesid+' [name=json_txt]').append('<p>'+JSON.stringify(json[oesid], null, '\t')+'</p>');
		$('#'+oesid+' [name=display]').text(json[oesid]["oesunit"]["display"]);
		// EMU
		$('#'+oesid+' [name=charge_discharge_power]').val(json[oesid]["emu"]["charge_discharge_power"]);
		$('#'+oesid+' [name=rsoc]').val(json[oesid]["emu"]["rsoc"]);
		$('#'+oesid+' [name=ups_output_power]').val(json[oesid]["emu"]["ups_output_power"]);
		$('#'+oesid+' [name=pvc_charge_power]').val(json[oesid]["emu"]["pvc_charge_power"]);
		// DCDC
		$('#'+oesid+' [name=status]').val(json[oesid]["dcdc"]["status"]["status"]);
		$('#'+oesid+' [name=dig]').val(json[oesid]["dcdc"]["param"]["dig"]);
		$('#'+oesid+' [name=dvg]').val(json[oesid]["dcdc"]["vdis"]["dvg"]);
		$('#'+oesid+' [name=drg]').val(json[oesid]["dcdc"]["vdis"]["drg"]);
		$('#'+oesid+' [name=p1]').val(json[oesid]["dcdc"]["powermeter"]["p1"]);
		$('#'+oesid+' [name=p2]').val(json[oesid]["dcdc"]["powermeter"]["p2"]);
		// METER
		updateMeter(oesid, json[oesid]);
	}
}

function updateJsonForm(form, id, json){
	$(form).find(".json_txt").empty();
	$(form).find(".json_txt").append('<h2>'+id+'</h2><hr>');
	$(form).find(".json_txt").append('<p>'+JSON.stringify(json, null, '\t')+'</p>');
}
