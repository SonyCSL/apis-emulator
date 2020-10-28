<!DOCTYPE html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<title>
{{ title }} </title>
<link rel="stylesheet" type="text/css" href="./css/style.css">
<!--[if lt IE 9]>
<script type="text/javascript">
alert("Your browser does not support the canvas tag.");
</script>
<![endif]-->
<script src="//code.jquery.com/jquery-1.7.2.js" crossorigin="anonymous"></script>
<script src="./js/main.js" type="text/javascript"></script>
</head>
<body>

<div id="content">

	<div class="field1 buttons">
		Auto Refresh :<input type="checkbox" id="auto_refresh" checked="checked" />
		<input type="button" class="read_all" value="Read All" />
		<input type="button" class="set_all" value="Set All" />
		<input type="button" class="save_all" value="Save All" />
		<input type="button" class="load_last" value="Load Last" />
		<input type="button" class="reset" value="Reset" />
		<input type="button" class="add_unit" value="Add Unit" />
		<input type="button" class="remove_unit" value="Remove Unit" />
		<input type="button" class="set_acc" value="Set Acceleration Rate:" />
		<input class="textfield" type="text" name="acc" id="acc" />
		
	</div><br>

%i=0
%for oesid in ids:
	<div id="field{{oesid}}" class="fields">
		<div id="counter" style="display: none;">{{i}}</div>
		<form id="{{oesid}}">
			<h1 class="ip">{{oesid}}</h1>
			<div name="display">{{oesid}}</div>

			<br>

			Charge discharge power : <input class="textfield" type="text" name="charge_discharge_power" id="charge_discharge_power" /><br />
			rsoc : <input class="textfield" type="text" name="rsoc" id="rsoc" /><br />
			ups output power : <input class="textfield" type="text" name="ups_output_power" id="ups_output_power" /><br />
			pvc charge power : <input class="textfield" type="text" name="pvc_charge_power" id="pvc_charge_power" /><br />
			Powermeter all : <input class="textfield" type="text" name="p1" id="p1" /><br />
			Powermeter p2 : <input class="textfield" type="text" name="p2" id="p2" /><br />
			Status : <input class="textfield" type="text" name="status" id="status" /><br />
			Grid current : <input class="textfield" type="text" name="dig" id="dig" /><br />
			Grid voltage : <input class="textfield" type="text" name="dvg" id="dvg" /><br />
			Droop ratio : <input class="textfield" type="text" name="drg" id="drg" /><br/>
			

			<div class="field1 buttons">
				<input type="button" class="read" value="Read" />
				<input type="button" class="set" value="Set" />
			</div><br>

			<div class="meter">
				<div class="meterelem">Grid voltage<br><div class="vg"></div></div>
				<div class="meterelem">Grid current<br><div class="ig"></div></div>
				<div class="meterelem">Grid power<br><div class="wg"></div></div><br>
				<div class="meterelem">Battery voltage<br><div class="vb"></div></div>
				<div class="meterelem">Battery current<br><div class="ib"></div></div>
				<div class="meterelem">Battery power<br><div class="wb"></div></div><br>
			</div>
			<div class="battery">Battery Status : </div>
			<div class="loss">DCDC Operating power : </div>
			<div class="charge_discharge_power">Charge discharge power : </div>
			<div class="ups_output_power">UPS output power : </div>
			<div class="pvc_charge_power">PVC charge power : </div>
			<div class="p1">Powermeter all : </div>
			<div class="p2">Powermeter p2 : </div>
			<div class="error emuerror"></div>
			<div class="error dcdcerror"></div>

			<div class="json_txt" name="json_txt" id="json_{{oesid}}"></div>
		</form>
	</div>
	%i=i+1
	%end

</div>
</body>
</html>
