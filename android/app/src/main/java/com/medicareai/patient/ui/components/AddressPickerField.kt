package com.medicareai.patient.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.medicareai.patient.data.model.ChinaAddressData
import com.medicareai.patient.data.model.City
import com.medicareai.patient.data.model.District
import com.medicareai.patient.data.model.Province
import com.medicareai.patient.ui.theme.PrimaryBlue

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddressPickerField(
    label: String,
    address: String,
    onAddressSelected: (province: String, city: String, district: String, fullAddress: String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "选择省市区"
) {
    var showAddressPicker by remember { mutableStateOf(false) }
    
    Box(modifier = modifier) {
        OutlinedTextField(
            value = address,
            onValueChange = { },
            label = { Text(label) },
            placeholder = { Text(placeholder) },
            leadingIcon = {
                Icon(Icons.Default.LocationOn, null, tint = PrimaryBlue)
            },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            singleLine = true,
            readOnly = true,
            trailingIcon = {
                IconButton(onClick = { showAddressPicker = true }) {
                    Icon(Icons.Default.KeyboardArrowDown, null)
                }
            }
        )
    }
    
    if (showAddressPicker) {
        AddressPickerDialog(
            onDismiss = { showAddressPicker = false },
            onConfirm = { province, city, district ->
                val fullAddress = "$province $city $district"
                onAddressSelected(province, city, district, fullAddress)
                showAddressPicker = false
            }
        )
    }
}

@Composable
private fun AddressPickerDialog(
    onDismiss: () -> Unit,
    onConfirm: (province: String, city: String, district: String) -> Unit
) {
    var selectedProvince by remember { mutableStateOf<Province?>(null) }
    var selectedCity by remember { mutableStateOf<City?>(null) }
    var selectedDistrict by remember { mutableStateOf<District?>(null) }
    
    var showProvinceList by remember { mutableStateOf(false) }
    var showCityList by remember { mutableStateOf(false) }
    var showDistrictList by remember { mutableStateOf(false) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 6.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
            ) {
                // Title
                Text(
                    text = "选择地址",
                    style = MaterialTheme.typography.titleLarge,
                    color = PrimaryBlue,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                // Province Selection Button
                OutlinedButton(
                    onClick = { showProvinceList = true },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = selectedProvince?.name ?: "请选择省份",
                        modifier = Modifier.weight(1f)
                    )
                    Icon(Icons.Default.KeyboardArrowDown, null)
                }
                Spacer(modifier = Modifier.height(12.dp))

                // City Selection Button
                OutlinedButton(
                    onClick = { if (selectedProvince != null) showCityList = true },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp),
                    enabled = selectedProvince != null
                ) {
                    Text(
                        text = selectedCity?.name ?: "请选择城市",
                        modifier = Modifier.weight(1f)
                    )
                    Icon(Icons.Default.KeyboardArrowDown, null)
                }
                Spacer(modifier = Modifier.height(12.dp))

                // District Selection Button
                OutlinedButton(
                    onClick = { if (selectedCity != null) showDistrictList = true },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(8.dp),
                    enabled = selectedCity != null
                ) {
                    Text(
                        text = selectedDistrict?.name ?: "请选择区县",
                        modifier = Modifier.weight(1f)
                    )
                    Icon(
                        Icons.Default.KeyboardArrowDown, 
                        null,
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }

                // Preview
                if (selectedProvince != null && selectedCity != null && selectedDistrict != null) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer
                        )
                    ) {
                        Text(
                            text = "已选择: ${selectedProvince?.name} ${selectedCity?.name} ${selectedDistrict?.name}",
                            modifier = Modifier.padding(12.dp),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    TextButton(onClick = onDismiss) {
                        Text("取消")
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(
                        onClick = {
                            if (selectedProvince != null && selectedCity != null && selectedDistrict != null) {
                                onConfirm(
                                    selectedProvince!!.name,
                                    selectedCity!!.name,
                                    selectedDistrict!!.name
                                )
                            }
                        },
                        enabled = selectedProvince != null && selectedCity != null && selectedDistrict != null,
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                    ) {
                        Text("确定")
                    }
                }
            }
        }
    }

    // Province Selection Dialog
    if (showProvinceList) {
        SelectionDialog(
            title = "选择省份",
            items = ChinaAddressData.provinces.map { it.name },
            onDismiss = { showProvinceList = false },
            onSelect = { provinceName ->
                selectedProvince = ChinaAddressData.provinces.find { it.name == provinceName }
                selectedCity = null
                selectedDistrict = null
                showProvinceList = false
            }
        )
    }

    // City Selection Dialog
    if (showCityList && selectedProvince != null) {
        SelectionDialog(
            title = "选择城市",
            items = selectedProvince!!.cities.map { it.name },
            onDismiss = { showCityList = false },
            onSelect = { cityName ->
                selectedCity = selectedProvince!!.cities.find { it.name == cityName }
                selectedDistrict = null
                showCityList = false
            }
        )
    }

    // District Selection Dialog
    if (showDistrictList && selectedCity != null) {
        SelectionDialog(
            title = "选择区县",
            items = selectedCity!!.districts.map { it.name },
            onDismiss = { showDistrictList = false },
            onSelect = { districtName ->
                selectedDistrict = selectedCity!!.districts.find { it.name == districtName }
                showDistrictList = false
            }
        )
    }
}

@Composable
private fun SelectionDialog(
    title: String,
    items: List<String>,
    onDismiss: () -> Unit,
    onSelect: (String) -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 6.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 500.dp)
                    .padding(16.dp)
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = PrimaryBlue,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                LazyColumn(
                    modifier = Modifier.weight(1f)
                ) {
                    items(items) { item ->
                        TextButton(
                            onClick = { onSelect(item) },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = item,
                                style = MaterialTheme.typography.bodyLarge,
                                modifier = Modifier.fillMaxWidth()
                            )
                        }
                        Divider(thickness = 0.5.dp)
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))
                TextButton(
                    onClick = onDismiss,
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text("取消")
                }
            }
        }
    }
}
