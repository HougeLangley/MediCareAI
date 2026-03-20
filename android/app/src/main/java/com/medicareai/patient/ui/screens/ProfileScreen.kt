package com.medicareai.patient.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.medicareai.patient.R
import com.medicareai.patient.data.model.ChronicDisease
import com.medicareai.patient.data.model.PatientChronicCondition
import com.medicareai.patient.ui.components.DatePickerField
import com.medicareai.patient.ui.theme.PrimaryBlue
import com.medicareai.patient.viewmodel.ChronicDiseaseViewModel
import com.medicareai.patient.viewmodel.ProfileViewModel
import com.medicareai.patient.viewmodel.UiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onNavigateBack: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel(),
    chronicDiseaseViewModel: ChronicDiseaseViewModel = hiltViewModel()
) {
    val profileState by viewModel.profileState.collectAsState()
    val updateState by viewModel.updateState.collectAsState()
    val myDiseases by chronicDiseaseViewModel.myDiseases.collectAsState()
    val availableDiseases by chronicDiseaseViewModel.availableDiseases.collectAsState()
    val addDiseaseState by chronicDiseaseViewModel.addDiseaseState.collectAsState()
    val deleteDiseaseState by chronicDiseaseViewModel.deleteDiseaseState.collectAsState()

    var isEditing by remember { mutableStateOf(false) }
    var showAddDiseaseDialog by remember { mutableStateOf(false) }

    val snackbarHostState = remember { SnackbarHostState() }

    var fullName by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var gender by remember { mutableStateOf("") }
    var dateOfBirth by remember { mutableStateOf("") }
    var address by remember { mutableStateOf("") }
    var emergencyContactName by remember { mutableStateOf("") }
    var emergencyContactPhone by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        viewModel.loadProfile()
        chronicDiseaseViewModel.loadMyDiseases()
        chronicDiseaseViewModel.loadAvailableDiseases()
    }

    LaunchedEffect(profileState) {
        if (profileState is UiState.Success) {
            val patient = (profileState as UiState.Success).data
            fullName = patient.user_full_name
            phone = patient.phone ?: ""
            gender = patient.gender ?: ""
            dateOfBirth = patient.date_of_birth ?: ""
            address = patient.address ?: ""
            emergencyContactName = patient.emergency_contact_name ?: ""
            emergencyContactPhone = patient.emergency_contact_phone ?: ""
            if (emergencyContactName.isEmpty() && emergencyContactPhone.isEmpty()) {
                patient.emergency_contact?.let { contact ->
                    val parts = contact.split(" ")
                    if (parts.isNotEmpty()) {
                        emergencyContactName = parts[0]
                    }
                    if (parts.size >= 2) {
                        emergencyContactPhone = parts[1]
                    }
                }
            }
        }
    }

    LaunchedEffect(addDiseaseState) {
        when (addDiseaseState) {
            is UiState.Success -> {
                snackbarHostState.showSnackbar("疾病添加成功")
                chronicDiseaseViewModel.clearAddState()
                showAddDiseaseDialog = false
            }
            is UiState.Error -> {
                snackbarHostState.showSnackbar("添加失败: ${(addDiseaseState as UiState.Error).message}")
                chronicDiseaseViewModel.clearAddState()
            }
            else -> {}
        }
    }

    LaunchedEffect(deleteDiseaseState) {
        when (deleteDiseaseState) {
            is UiState.Success -> {
                snackbarHostState.showSnackbar("疾病已删除")
                chronicDiseaseViewModel.clearDeleteState()
            }
            is UiState.Error -> {
                snackbarHostState.showSnackbar("删除失败: ${(deleteDiseaseState as UiState.Error).message}")
                chronicDiseaseViewModel.clearDeleteState()
            }
            else -> {}
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.profile)) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, null)
                    }
                },
                actions = {
                    if (profileState is UiState.Success) {
                        IconButton(onClick = { isEditing = !isEditing }) {
                            Icon(
                                if (isEditing) Icons.Default.Close else Icons.Default.Edit,
                                null
                            )
                        }
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (profileState) {
                is UiState.Loading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                is UiState.Error -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = (profileState as UiState.Error).message,
                            color = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { viewModel.loadProfile() }) {
                            Text("重试")
                        }
                    }
                }
                is UiState.Success -> {
                    val patient = (profileState as UiState.Success).data

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                            .padding(16.dp)
                    ) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(24.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Surface(
                                    shape = androidx.compose.foundation.shape.CircleShape,
                                    color = PrimaryBlue.copy(alpha = 0.1f),
                                    modifier = Modifier.size(100.dp)
                                ) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Text(
                                            text = patient.user_full_name.firstOrNull()?.toString() ?: "患",
                                            style = MaterialTheme.typography.displayLarge,
                                            color = PrimaryBlue
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(16.dp))

                                Text(
                                    text = patient.user_full_name,
                                    style = MaterialTheme.typography.headlineSmall,
                                    fontWeight = FontWeight.Bold
                                )

                                Text(
                                    text = "患者 ID: ${patient.id.take(8)}...",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Color.Gray
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp)
                            ) {
                                if (updateState is UiState.Success) {
                                    Text(
                                        text = "更新成功",
                                        color = Color(0xFF28a745),
                                        modifier = Modifier.padding(bottom = 8.dp)
                                    )
                                }

                                ProfileField(
                                    label = "姓名",
                                    value = fullName,
                                    onValueChange = { fullName = it },
                                    icon = Icons.Default.Person,
                                    enabled = isEditing
                                )

                                ProfileField(
                                    label = "邮箱",
                                    value = patient.user_id,
                                    onValueChange = {},
                                    icon = Icons.Default.Email,
                                    enabled = false
                                )

                                ProfileField(
                                    label = "性别",
                                    value = gender,
                                    onValueChange = { gender = it },
                                    icon = Icons.Default.PersonOutline,
                                    enabled = isEditing
                                )

                                ProfileField(
                                    label = "出生日期",
                                    value = dateOfBirth,
                                    onValueChange = { dateOfBirth = it },
                                    icon = Icons.Default.CalendarToday,
                                    enabled = isEditing,
                                    placeholder = "YYYY-MM-DD"
                                )

                                ProfileField(
                                    label = "手机号码",
                                    value = phone,
                                    onValueChange = { phone = it },
                                    icon = Icons.Default.Phone,
                                    enabled = isEditing
                                )

                                ProfileField(
                                    label = "地址",
                                    value = address,
                                    onValueChange = { address = it },
                                    icon = Icons.Default.LocationOn,
                                    enabled = isEditing
                                )

                                ProfileField(
                                    label = "紧急联系人姓名",
                                    value = emergencyContactName,
                                    onValueChange = { emergencyContactName = it },
                                    icon = Icons.Default.ContactPhone,
                                    enabled = isEditing
                                )

                                ProfileField(
                                    label = "紧急联系人电话",
                                    value = emergencyContactPhone,
                                    onValueChange = { emergencyContactPhone = it },
                                    icon = Icons.Default.Phone,
                                    enabled = isEditing
                                )
                            }
                        }

                        if (isEditing) {
                            Spacer(modifier = Modifier.height(16.dp))

                            Button(
                                onClick = {
                                    viewModel.updateProfile(
                                        com.medicareai.patient.data.model.PatientUpdateRequest(
                                            gender = gender.takeIf { it.isNotEmpty() },
                                            phone = phone.takeIf { it.isNotEmpty() },
                                            address = address.takeIf { it.isNotEmpty() },
                                            emergency_contact_name = emergencyContactName.takeIf { it.isNotEmpty() },
                                            emergency_contact_phone = emergencyContactPhone.takeIf { it.isNotEmpty() }
                                        )
                                    )
                                    isEditing = false
                                },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                if (updateState is UiState.Loading) {
                                    CircularProgressIndicator(
                                        color = Color.White,
                                        modifier = Modifier.size(24.dp)
                                    )
                                } else {
                                    Text("保存修改")
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        ChronicDiseaseSection(
                            myDiseases = myDiseases,
                            onAddClick = { showAddDiseaseDialog = true },
                            onDeleteClick = { conditionId ->
                                chronicDiseaseViewModel.deleteChronicDisease(conditionId)
                            }
                        )

                        Spacer(modifier = Modifier.height(24.dp))
                    }
                }
                else -> {}
            }
        }

        if (showAddDiseaseDialog) {
            AddChronicDiseaseDialog(
                availableDiseases = availableDiseases,
                onDismiss = { showAddDiseaseDialog = false },
                onConfirm = { diseaseId, severity, diagnosisDate, notes ->
                    chronicDiseaseViewModel.addChronicDisease(diseaseId, diagnosisDate, severity, notes)
                }
            )
        }
    }
}

@Composable
private fun ChronicDiseaseSection(
    myDiseases: UiState<List<PatientChronicCondition>>,
    onAddClick: () -> Unit,
    onDeleteClick: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "特殊病与慢性病管理",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )

                IconButton(onClick = onAddClick) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "添加疾病",
                        tint = PrimaryBlue
                    )
                }
            }

            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFFFFF3CD),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = "如果您患有特殊病或慢性病，请务必如实填写。这将帮助AI在诊断时考虑您的病史，避免药物相互作用等风险。",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF856404),
                    modifier = Modifier.padding(12.dp)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            when (myDiseases) {
                is UiState.Loading -> {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                is UiState.Error -> {
                    Text(
                        text = "加载失败: ${myDiseases.message}",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                is UiState.Success -> {
                    val diseases = myDiseases.data
                    if (diseases.isEmpty()) {
                        Text(
                            text = "暂无记录，请点击右上角添加",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.Gray,
                            modifier = Modifier.padding(vertical = 16.dp)
                        )
                    } else {
                        Column(
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            diseases.forEach { condition ->
                                ChronicDiseaseChip(
                                    condition = condition,
                                    onDelete = { onDeleteClick(condition.id) }
                                )
                            }
                        }
                    }
                }
                else -> {}
            }
        }
    }
}

@Composable
private fun ChronicDiseaseChip(
    condition: PatientChronicCondition,
    onDelete: () -> Unit
) {
    val disease = condition.disease
    val diseaseName = disease?.common_names?.firstOrNull()
        ?: disease?.icd10_name
        ?: "未知疾病"

    val backgroundColor = when (disease?.disease_type) {
        "special" -> Color(0xFFFFF3CD)
        "chronic" -> Color(0xFFD1ECF1)
        "both" -> Color(0xFFF8D7DA)
        else -> Color(0xFFF8F9FA)
    }

    val textColor = when (disease?.disease_type) {
        "special" -> Color(0xFF856404)
        "chronic" -> Color(0xFF0C5460)
        "both" -> Color(0xFF721C24)
        else -> Color.DarkGray
    }

    val typeLabel = when (disease?.disease_type) {
        "special" -> "特殊病"
        "chronic" -> "慢性病"
        "both" -> "特殊病+慢性病"
        else -> ""
    }

    val severityLabel = when (condition.severity) {
        "mild" -> "轻度"
        "moderate" -> "中度"
        "severe" -> "重度"
        else -> null
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = backgroundColor,
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = diseaseName,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = textColor
                )
                Text(
                    text = buildString {
                        append(typeLabel)
                        if (severityLabel != null) {
                            append(" - ")
                            append(severityLabel)
                        }
                        if (!condition.diagnosis_date.isNullOrEmpty()) {
                            append(" | 确诊: ")
                            append(condition.diagnosis_date)
                        }
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = textColor.copy(alpha = 0.8f)
                )
            }

            IconButton(
                onClick = onDelete,
                modifier = Modifier.size(32.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Delete,
                    contentDescription = "删除",
                    tint = textColor,
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AddChronicDiseaseDialog(
    availableDiseases: UiState<List<ChronicDisease>>,
    onDismiss: () -> Unit,
    onConfirm: (String, String?, String?, String?) -> Unit
) {
    var selectedDiseaseId by remember { mutableStateOf<String?>(null) }
    var selectedSeverity by remember { mutableStateOf("") }
    var diagnosisDate by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }
    var expanded by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加疾病") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                when (availableDiseases) {
                    is UiState.Loading -> {
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator()
                        }
                    }
                    is UiState.Error -> {
                        Text(
                            text = "加载疾病列表失败",
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                    is UiState.Success -> {
                        val diseases = availableDiseases.data
                        ExposedDropdownMenuBox(
                            expanded = expanded,
                            onExpandedChange = { expanded = it }
                        ) {
                            OutlinedTextField(
                                value = diseases.find { it.id == selectedDiseaseId }?.let {
                                    it.common_names?.firstOrNull() ?: it.icd10_name
                                } ?: "",
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("选择疾病 *") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .menuAnchor(),
                                shape = RoundedCornerShape(12.dp)
                            )

                            ExposedDropdownMenu(
                                expanded = expanded,
                                onDismissRequest = { expanded = false }
                            ) {
                                diseases.forEach { disease ->
                                    val displayName = disease.common_names?.firstOrNull()
                                        ?: disease.icd10_name
                                    DropdownMenuItem(
                                        text = {
                                            Column {
                                                Text(displayName)
                                                Text(
                                                    "${disease.icd10_code} (${getDiseaseTypeLabel(disease.disease_type)})",
                                                    style = MaterialTheme.typography.bodySmall,
                                                    color = Color.Gray
                                                )
                                            }
                                        },
                                        onClick = {
                                            selectedDiseaseId = disease.id
                                            expanded = false
                                        }
                                    )
                                }
                            }
                        }
                    }
                    else -> {}
                }

                var severityExpanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = severityExpanded,
                    onExpandedChange = { severityExpanded = it }
                ) {
                    OutlinedTextField(
                        value = when (selectedSeverity) {
                            "mild" -> "轻度"
                            "moderate" -> "中度"
                            "severe" -> "重度"
                            else -> ""
                        },
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("严重程度") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = severityExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor(),
                        shape = RoundedCornerShape(12.dp)
                    )

                    ExposedDropdownMenu(
                        expanded = severityExpanded,
                        onDismissRequest = { severityExpanded = false }
                    ) {
                        listOf(
                            "mild" to "轻度",
                            "moderate" to "中度",
                            "severe" to "重度"
                        ).forEach { (value, label) ->
                            DropdownMenuItem(
                                text = { Text(label) },
                                onClick = {
                                    selectedSeverity = value
                                    severityExpanded = false
                                }
                            )
                        }
                    }
                }

                DatePickerField(
                    label = "确诊日期",
                    selectedDate = diagnosisDate,
                    onDateSelected = { diagnosisDate = it },
                    modifier = Modifier.fillMaxWidth()
                )

                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text("备注说明") },
                    placeholder = { Text("可选：补充说明病情、用药情况等") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    minLines = 2
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    selectedDiseaseId?.let { diseaseId ->
                        onConfirm(
                            diseaseId,
                            selectedSeverity.takeIf { it.isNotEmpty() },
                            diagnosisDate.takeIf { it.isNotEmpty() },
                            notes.takeIf { it.isNotEmpty() }
                        )
                    }
                },
                enabled = selectedDiseaseId != null
            ) {
                Text("添加")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}

private fun getDiseaseTypeLabel(type: String): String {
    return when (type) {
        "special" -> "特殊病"
        "chronic" -> "慢性病"
        "both" -> "特殊病+慢性病"
        else -> type
    }
}

@Composable
private fun ProfileField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    enabled: Boolean,
    placeholder: String = ""
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        leadingIcon = { Icon(icon, null, tint = PrimaryBlue) },
        enabled = enabled,
        placeholder = { Text(placeholder) },
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        shape = RoundedCornerShape(12.dp),
        singleLine = true
    )
}
