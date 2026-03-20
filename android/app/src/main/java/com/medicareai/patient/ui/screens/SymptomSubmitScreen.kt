package com.medicareai.patient.ui.screens

import android.app.DatePickerDialog
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.hilt.navigation.compose.hiltViewModel
import com.medicareai.patient.R
import com.medicareai.patient.data.model.Doctor
import com.medicareai.patient.data.model.KnowledgeSource
import com.medicareai.patient.ui.theme.PrimaryBlue
import com.medicareai.patient.ui.theme.PrimaryPurple
import com.medicareai.patient.viewmodel.StreamingDiagnosisState
import com.medicareai.patient.viewmodel.SymptomSubmitViewModel
import com.medicareai.patient.viewmodel.UiState
import java.io.File
import java.text.SimpleDateFormat
import java.util.*


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SymptomSubmitScreen(
    onNavigateBack: () -> Unit,
    viewModel: SymptomSubmitViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    
    // Form state
    var symptoms by remember { mutableStateOf("") }
    var durationValue by remember { mutableStateOf("") }
    var durationUnit by remember { mutableStateOf("天") }
    var severity by remember { mutableStateOf("") }
    var onsetDate by remember { mutableStateOf<Date?>(null) }
    var triggers by remember { mutableStateOf("") }
    var previousDiseases by remember { mutableStateOf("") }
    var shareWithDoctors by remember { mutableStateOf(false) }
    
    val submitState by viewModel.submitState.collectAsState()
    val streamingState by viewModel.streamingState.collectAsState()
    val uploadState by viewModel.uploadState.collectAsState()
    val uploadProgress by viewModel.uploadProgress.collectAsState()
    val selectedFiles by viewModel.selectedFiles.collectAsState()
    val doctorsState by viewModel.doctorsState.collectAsState()
    val selectedDoctors by viewModel.selectedDoctors.collectAsState()
    
    // Dialog states
    var showDoctorDialog by remember { mutableStateOf(false) }

    // Dropdown states
    var severityExpanded by remember { mutableStateOf(false) }
    var durationUnitExpanded by remember { mutableStateOf(false) }
    
    val severities = listOf("轻微", "轻度", "中度", "重度", "严重")
    val durationUnits = listOf("秒", "分钟", "小时", "天", "周", "月")
    
    // Load doctors when screen opens
    LaunchedEffect(Unit) {
        viewModel.loadDoctors()
    }
    
    // Date picker
    val calendar = Calendar.getInstance()
    val datePickerDialog = remember {
        DatePickerDialog(
            context,
            { _, year, month, dayOfMonth ->
                calendar.set(year, month, dayOfMonth)
                onsetDate = calendar.time
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        )
    }
    
    val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.symptom_submit)) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, null)
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Symptom Description
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "症状描述",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedTextField(
                        value = symptoms,
                        onValueChange = { symptoms = it },
                        label = { Text("主要症状（必填）") },
                        placeholder = { Text(stringResource(R.string.symptom_hint)) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp),
                        shape = RoundedCornerShape(12.dp),
                        maxLines = 4
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Duration and Severity
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "症状详情",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Duration with Value and Unit
                    Text(
                        text = "症状持续时间",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.Gray,
                        modifier = Modifier.padding(bottom = 4.dp)
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Duration Value Input
                        OutlinedTextField(
                            value = durationValue,
                            onValueChange = { 
                                if (it.isEmpty() || it.matches(Regex("^\\d*$"))) {
                                    durationValue = it
                                }
                            },
                            label = { Text("数值") },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(12.dp),
                            singleLine = true
                        )
                        
                        // Duration Unit Dropdown
                        ExposedDropdownMenuBox(
                            expanded = durationUnitExpanded,
                            onExpandedChange = { durationUnitExpanded = it },
                            modifier = Modifier.weight(1f)
                        ) {
                            OutlinedTextField(
                                value = durationUnit,
                                onValueChange = {},
                                label = { Text("单位") },
                                readOnly = true,
                                modifier = Modifier.menuAnchor(),
                                shape = RoundedCornerShape(12.dp),
                                trailingIcon = {
                                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = durationUnitExpanded)
                                }
                            )
                            
                            ExposedDropdownMenu(
                                expanded = durationUnitExpanded,
                                onDismissRequest = { durationUnitExpanded = false }
                            ) {
                                durationUnits.forEach { unit ->
                                    DropdownMenuItem(
                                        text = { Text(unit) },
                                        onClick = {
                                            durationUnit = unit
                                            durationUnitExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Severity Dropdown
                    ExposedDropdownMenuBox(
                        expanded = severityExpanded,
                        onExpandedChange = { severityExpanded = it }
                    ) {
                        OutlinedTextField(
                            value = severity,
                            onValueChange = {},
                            label = { Text(stringResource(R.string.severity)) },
                            readOnly = true,
                            modifier = Modifier
                                .fillMaxWidth()
                                .menuAnchor(),
                            shape = RoundedCornerShape(12.dp),
                            trailingIcon = {
                                ExposedDropdownMenuDefaults.TrailingIcon(expanded = severityExpanded)
                            }
                        )
                        
                        ExposedDropdownMenu(
                            expanded = severityExpanded,
                            onDismissRequest = { severityExpanded = false }
                        ) {
                            severities.forEach { s ->
                                DropdownMenuItem(
                                    text = { Text(s) },
                                    onClick = {
                                        severity = s
                                        severityExpanded = false
                                    }
                                )
                            }
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Additional Information
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "其他信息",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Onset Time - Date Picker
                    OutlinedTextField(
                        value = onsetDate?.let { dateFormat.format(it) } ?: "",
                        onValueChange = {},
                        label = { Text("发病时间") },
                        placeholder = { Text("点击选择日期") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        readOnly = true,
                        trailingIcon = {
                            IconButton(onClick = { datePickerDialog.show() }) {
                                Icon(Icons.Default.CalendarToday, null)
                            }
                        }
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedTextField(
                        value = triggers,
                        onValueChange = { triggers = it },
                        label = { Text("诱因（如果知道）") },
                        placeholder = { Text("例如：接触过敏原、气候变化、运动后等") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        maxLines = 2
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedTextField(
                        value = previousDiseases,
                        onValueChange = { previousDiseases = it },
                        label = { Text("既往史相关疾病（可选）") },
                        placeholder = { Text("例如：曾经患过类似症状的疾病") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        maxLines = 2
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // File Upload Section
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "检查资料上传",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // File picker launcher
                    val filePickerLauncher = rememberLauncherForActivityResult(
                        contract = ActivityResultContracts.GetMultipleContents()
                    ) { uris ->
                        uris.forEach { uri ->
                            context.contentResolver.openInputStream(uri)?.use { input ->
                                val tempFile = File(context.cacheDir, getFileName(context, uri) ?: "document")
                                tempFile.outputStream().use { output ->
                                    input.copyTo(output)
                                }
                                viewModel.addSelectedFile(tempFile)
                            }
                        }
                    }
                    
                    // Selected files display
                    if (selectedFiles.isNotEmpty()) {
                        Column {
                            selectedFiles.forEach { file ->
                                val progress = uploadProgress[file.name] ?: 0f
                                FileUploadItem(
                                    fileName = file.name,
                                    fileSize = formatFileSize(file.length()),
                                    progress = progress,
                                    onRemove = { viewModel.removeSelectedFile(file) }
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                            }
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                    }
                    
                    // Upload button
                    OutlinedButton(
                        onClick = { filePickerLauncher.launch("*/*") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.AttachFile, null, modifier = Modifier.padding(end = 8.dp))
                        Text("选择文件 (PDF/图片/文档)")
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "单个文件大小不得超过 10MB",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )

                    if (uploadState is UiState.Error) {
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = (uploadState as UiState.Error).message,
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // @ Doctor Section
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "@提及医生",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "选择医生后，他们可以看到您的症状和诊断结果",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Selected doctors chips
                    if (selectedDoctors.isNotEmpty()) {
                        FlowRow(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            selectedDoctors.forEach { doctor ->
                                DoctorChip(
                                    doctor = doctor,
                                    onRemove = { viewModel.unselectDoctor(doctor) }
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                    }
                    
                    // Add doctor button
                    OutlinedButton(
                        onClick = { showDoctorDialog = true },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.PersonAdd, null, modifier = Modifier.padding(end = 8.dp))
                        Text("选择医生")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Doctor Selection Dialog
            if (showDoctorDialog) {
                DoctorSelectionDialog(
                    doctors = when (val state = doctorsState) {
                        is UiState.Success -> state.data
                        else -> emptyList()
                    },
                    selectedDoctors = selectedDoctors,
                    isLoading = doctorsState is UiState.Loading,
                    onDismiss = { showDoctorDialog = false },
                    onDoctorSelected = { doctor ->
                        viewModel.selectDoctor(doctor)
                    },
                    onDoctorUnselected = { doctor ->
                        viewModel.unselectDoctor(doctor)
                    }
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Privacy Consent
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "隐私授权",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = shareWithDoctors,
                            onCheckedChange = { shareWithDoctors = it },
                            colors = CheckboxDefaults.colors(checkedColor = PrimaryBlue)
                        )
                        Column(
                            modifier = Modifier.weight(1f)
                        ) {
                            Text(
                                text = "允许将本次诊断信息共享给医生端",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Medium
                            )
                            Text(
                                text = "勾选后，医生可以查看您的症状、AI诊断结果和上传的检查资料（个人敏感信息将被自动隐藏）。不勾选则仅您自己可见。",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.Gray
                            )
                        }
                    }
                }
            }
            
            // Show file upload progress when uploading
            if (streamingState.isLoading && selectedFiles.isNotEmpty()) {
                Spacer(modifier = Modifier.height(16.dp))
                
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFE3F2FD)
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "文件上传和处理进度",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        selectedFiles.forEach { file ->
                            val progress = uploadProgress[file.name] ?: 0f
                            val isUploaded = progress >= 1f
                            
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = if (isUploaded) Icons.Default.CheckCircle else Icons.Default.AttachFile,
                                    contentDescription = null,
                                    tint = if (isUploaded) Color(0xFF4CAF50) else Color.Gray,
                                    modifier = Modifier.size(20.dp)
                                )
                                
                                Spacer(modifier = Modifier.width(8.dp))
                                
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = file.name,
                                        style = MaterialTheme.typography.bodySmall,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    
                                    if (!isUploaded) {
                                        LinearProgressIndicator(
                                            progress = { progress },
                                            modifier = Modifier.fillMaxWidth(),
                                            color = PrimaryBlue
                                        )
                                    } else {
                                        Text(
                                            text = "上传完成，等待处理...",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = Color.Gray
                                        )
                                    }
                                }
                            }
                            
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Submit Button
            Button(
                onClick = {
                    val duration = if (durationValue.isNotEmpty()) "${durationValue}${durationUnit}" else null
                    val onsetTime = onsetDate?.let { dateFormat.format(it) }
                    val description = buildString {
                        if (triggers.isNotEmpty()) append("诱因: $triggers")
                        if (previousDiseases.isNotEmpty()) {
                            if (isNotEmpty()) append(" | ")
                            append("既往病史: $previousDiseases")
                        }
                    }.takeIf { it.isNotEmpty() } ?: ""
                    
                    val title = "AI诊断 - ${severity}" + 
                        if (durationValue.isNotEmpty()) " - ${durationValue}${durationUnit}" else ""
                    
                    viewModel.submitSymptoms(
                        title = title,
                        symptoms = symptoms,
                        severity = severity,
                        description = description,
                        onsetTime = onsetTime,
                        duration = duration
                    )
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                enabled = symptoms.isNotBlank() && !streamingState.isLoading,
                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryBlue
                )
            ) {
                if (streamingState.isLoading) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = streamingState.status.takeIf { it.isNotBlank() } ?: "处理中...",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White
                        )
                    }
                } else {
                    Icon(Icons.Default.Send, null, modifier = Modifier.padding(end = 8.dp))
                    Text("提交给AI诊断", style = MaterialTheme.typography.titleMedium)
                }
            }
            
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Reset Button
            OutlinedButton(
                onClick = {
                    symptoms = ""
                    durationValue = ""
                    durationUnit = "天"
                    severity = ""
                    onsetDate = null
                    triggers = ""
                    previousDiseases = ""
                    shareWithDoctors = false
                    viewModel.clearStates()
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Refresh, null, modifier = Modifier.padding(end = 8.dp))
                Text(stringResource(R.string.reset))
            }
            
            // Show error if submission failed
            if (submitState is UiState.Error) {
                Spacer(modifier = Modifier.height(8.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    ),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = (submitState as UiState.Error).message,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.padding(12.dp),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
            
            // Streaming Diagnosis Result
            if (streamingState.isLoading || streamingState.content.isNotEmpty() || streamingState.isComplete) {
                Spacer(modifier = Modifier.height(24.dp))
                
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFF0F8FF)
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "🤖 ",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = "AI诊断结果",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        // Progress indicator when loading
                        if (streamingState.isLoading) {
                            LinearProgressIndicator(
                                modifier = Modifier.fillMaxWidth(),
                                color = PrimaryBlue
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = streamingState.status,
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.Gray
                            )
                        }
                        
                        // Diagnosis Content
                        if (streamingState.content.isNotEmpty()) {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(8.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = Color.White
                                )
                            ) {
                                SimpleMarkdownContent(
                                    content = streamingState.content,
                                    modifier = Modifier.padding(12.dp)
                                )
                            }
                        }
                        
                        if (streamingState.isComplete) {
                            Spacer(modifier = Modifier.height(16.dp))
                            
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(12.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = Color(0xFFE3F2FD)
                                )
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(16.dp),
                                    horizontalArrangement = Arrangement.SpaceAround
                                ) {
                                    // Model Info
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Box(
                                            modifier = Modifier
                                                .size(44.dp)
                                                .background(
                                                    brush = androidx.compose.ui.graphics.Brush.linearGradient(
                                                        colors = listOf(PrimaryBlue, PrimaryPurple)
                                                    ),
                                                    shape = RoundedCornerShape(12.dp)
                                                ),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text("🤖", fontSize = MaterialTheme.typography.titleMedium.fontSize)
                                        }
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "AI 模型",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = Color.Gray
                                        )
                                        Text(
                                            text = streamingState.modelId ?: "未知模型",
                                            style = MaterialTheme.typography.bodySmall,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                    
                                    // Token Info
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Box(
                                            modifier = Modifier
                                                .size(44.dp)
                                                .background(
                                                    brush = androidx.compose.ui.graphics.Brush.linearGradient(
                                                        colors = listOf(Color(0xFF10B981), Color(0xFF059669))
                                                    ),
                                                    shape = RoundedCornerShape(12.dp)
                                                ),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text("🪙", fontSize = MaterialTheme.typography.titleMedium.fontSize)
                                        }
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "Token 消耗",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = Color.Gray
                                        )
                                        Text(
                                            text = streamingState.tokensUsed?.toString() ?: "N/A",
                                            style = MaterialTheme.typography.bodySmall,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                }
                            }
                            
                            // Knowledge Sources (Collapsible)
                            if (streamingState.knowledgeSources.isNotEmpty()) {
                                Spacer(modifier = Modifier.height(12.dp))
                                KnowledgeSourcesSection(sources = streamingState.knowledgeSources)
                            }
                        }
                        
                        // Error Message
                        streamingState.error?.let { error ->
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = error,
                                color = MaterialTheme.colorScheme.error,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun KnowledgeSourcesSection(sources: List<KnowledgeSource>) {
    var expanded by remember { mutableStateOf(false) }
    
    val totalChunks = sources.sumOf { it.chunks?.size ?: 0 }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFFAFAFA)
        )
    ) {
        Column {
            // Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { expanded = !expanded }
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "📚 ",
                    style = MaterialTheme.typography.titleMedium
                )
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "RAG 知识库引用",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "基于 $totalChunks 个相关医疗知识片段",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
                Icon(
                    if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (expanded) "Collapse" else "Expand"
                )
            }
            
            // Expanded Content
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    sources.forEach { source ->
                        source.chunks?.forEach { chunk ->
                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                shape = RoundedCornerShape(8.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = Color.White
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(12.dp)
                                ) {
                                    // Title and Score
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(
                                            text = chunk.document_title ?: "未知文档",
                                            style = MaterialTheme.typography.labelMedium,
                                            fontWeight = FontWeight.Bold,
                                            color = PrimaryBlue,
                                            modifier = Modifier.weight(1f)
                                        )
                                        chunk.relevance_score?.let { score ->
                                            val percentage = (score * 100).toInt()
                                            val color = when {
                                                percentage >= 80 -> Color(0xFF4CAF50)
                                                percentage >= 60 -> Color(0xFFFFA000)
                                                else -> Color(0xFFE53935)
                                            }
                                            Surface(
                                                shape = RoundedCornerShape(4.dp),
                                                color = color.copy(alpha = 0.1f)
                                            ) {
                                                Text(
                                                    text = "$percentage% 相关",
                                                    style = MaterialTheme.typography.labelSmall,
                                                    color = color,
                                                    fontWeight = FontWeight.Bold,
                                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                                )
                                            }
                                        }
                                    }
                                    
                                    // Section Title
                                    chunk.section_title?.let {
                                        Text(
                                            text = "📖 $it",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = Color.Gray,
                                            modifier = Modifier.padding(top = 4.dp)
                                        )
                                    }
                                    
                                    // Content Preview
                                    val text = chunk.chunk_text ?: chunk.text_preview ?: ""
                                    if (text.isNotEmpty()) {
                                        Text(
                                            text = if (text.length > 200) text.take(200) + "..." else text,
                                            style = MaterialTheme.typography.bodySmall,
                                            color = Color.DarkGray,
                                            modifier = Modifier.padding(top = 8.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// File Upload Item Component
@Composable
fun FileUploadItem(
    fileName: String,
    fileSize: String,
    progress: Float,
    onRemove: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFF5F5F5)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // File icon
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(PrimaryBlue.copy(alpha = 0.1f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.InsertDriveFile,
                    contentDescription = null,
                    tint = PrimaryBlue,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            // File info
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = fileName,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = fileSize,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
                
                // Progress bar
                if (progress > 0 && progress < 1f) {
                    Spacer(modifier = Modifier.height(4.dp))
                    LinearProgressIndicator(
                        progress = { progress },
                        modifier = Modifier.fillMaxWidth(),
                        color = PrimaryBlue
                    )
                    Text(
                        text = "${(progress * 100).toInt()}%",
                        style = MaterialTheme.typography.labelSmall,
                        color = PrimaryBlue
                    )
                }
            }
            
            // Remove button
            IconButton(onClick = onRemove) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Remove",
                    tint = Color.Gray
                )
            }
        }
    }
}

// Doctor Chip Component
@Composable
fun DoctorChip(
    doctor: Doctor,
    onRemove: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = PrimaryBlue.copy(alpha = 0.1f),
        border = androidx.compose.foundation.BorderStroke(1.dp, PrimaryBlue.copy(alpha = 0.3f))
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                tint = PrimaryBlue,
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = doctor.display_name,
                style = MaterialTheme.typography.bodySmall,
                color = PrimaryBlue,
                fontWeight = FontWeight.Medium
            )
            if (doctor.hospital != null) {
                Text(
                    text = " · ${doctor.hospital}",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.Gray,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
            Spacer(modifier = Modifier.width(4.dp))
            IconButton(
                onClick = onRemove,
                modifier = Modifier.size(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Remove",
                    tint = Color.Gray,
                    modifier = Modifier.size(14.dp)
                )
            }
        }
    }
}

// Doctor Selection Dialog
@Composable
fun DoctorSelectionDialog(
    doctors: List<Doctor>,
    selectedDoctors: List<Doctor>,
    isLoading: Boolean,
    onDismiss: () -> Unit,
    onDoctorSelected: (Doctor) -> Unit,
    onDoctorUnselected: (Doctor) -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 8.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    text = "选择医生",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "选择您想要分享诊断结果的医生",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                if (isLoading) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = PrimaryBlue)
                    }
                } else if (doctors.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "暂无可选医生",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.Gray
                        )
                    }
                } else {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(max = 300.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        doctors.forEach { doctor ->
                            val isSelected = selectedDoctors.any { it.id == doctor.id }
                            DoctorListItem(
                                doctor = doctor,
                                isSelected = isSelected,
                                onToggle = {
                                    if (isSelected) {
                                        onDoctorUnselected(doctor)
                                    } else {
                                        onDoctorSelected(doctor)
                                    }
                                }
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Close button
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("完成")
                }
            }
        }
    }
}

// Doctor List Item
@Composable
fun DoctorListItem(
    doctor: Doctor,
    isSelected: Boolean,
    onToggle: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onToggle)
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = isSelected,
            onCheckedChange = { onToggle() },
            colors = CheckboxDefaults.colors(checkedColor = PrimaryBlue)
        )
        
        Spacer(modifier = Modifier.width(8.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = doctor.display_name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            if (doctor.hospital != null || doctor.department != null) {
                Text(
                    text = listOfNotNull(doctor.hospital, doctor.department).joinToString(" · "),
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
            if (doctor.specialty != null) {
                Text(
                    text = doctor.specialty,
                    style = MaterialTheme.typography.labelSmall,
                    color = Color(0xFF1976D2)
                )
            }
        }
    }
}

// FlowRow layout for chips - simplified version
@Composable
fun FlowRow(
    modifier: Modifier = Modifier,
    horizontalArrangement: Arrangement.Horizontal = Arrangement.Start,
    verticalArrangement: Arrangement.Vertical = Arrangement.Top,
    content: @Composable () -> Unit
) {
    // Simplified flow layout - just use Column for now
    Column(
        modifier = modifier,
        verticalArrangement = verticalArrangement
    ) {
        content()
    }
}

// Simple Markdown Text Component
@Composable
fun MarkdownText(
    text: String,
    modifier: Modifier = Modifier,
    style: TextStyle = MaterialTheme.typography.bodyMedium
) {
    val annotatedString = buildAnnotatedString {
        var currentIndex = 0
        
        // Pattern for bold text: **text**
        val boldPattern = "\\*\\*(.*?)\\*\\*".toRegex()
        
        // Find all bold matches and build styled text
        val matches = boldPattern.findAll(text).toList()
        
        if (matches.isEmpty()) {
            // No bold formatting, just append plain text
            append(text)
        } else {
            var lastEnd = 0
            
            matches.forEach { match ->
                // Append text before this match
                if (match.range.first > lastEnd) {
                    append(text.substring(lastEnd, match.range.first))
                }
                
                // Append bold text (remove ** markers)
                val boldText = match.groupValues[1]
                withStyle(SpanStyle(fontWeight = FontWeight.Bold)) {
                    append(boldText)
                }
                
                lastEnd = match.range.last + 1
            }
            
            // Append remaining text
            if (lastEnd < text.length) {
                append(text.substring(lastEnd))
            }
        }
    }
    
    Text(
        text = annotatedString,
        modifier = modifier,
        style = style
    )
}

// Simple Markdown parser for headers and basic formatting
@Composable
fun SimpleMarkdownContent(
    content: String,
    modifier: Modifier = Modifier
) {
    val lines = content.lines()
    
    Column(modifier = modifier) {
        lines.forEach { line ->
            val trimmedLine = line.trim()
            when {
                // Table row - render as a styled row
                trimmedLine.startsWith("|") && trimmedLine.contains("|") -> {
                    // Skip table separator lines (| :--- | :--- |)
                    if (!trimmedLine.contains(":---") && !trimmedLine.contains("----")) {
                        // Parse table cells
                        val cells = trimmedLine.trim('|').split("|").map { it.trim() }
                        if (cells.isNotEmpty()) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceEvenly
                            ) {
                                cells.forEach { cell ->
                                    // Remove bold markers from cell content
                                    val cleanCell = cell.removeSurrounding("**", "**").let { inner ->
                                        if (inner != cell) inner else cell
                                    }
                                    Text(
                                        text = cleanCell,
                                        style = MaterialTheme.typography.bodySmall,
                                        fontWeight = if (cell.startsWith("**") && cell.endsWith("**")) FontWeight.Bold else FontWeight.Normal,
                                        modifier = Modifier
                                            .weight(1f)
                                            .padding(horizontal = 4.dp),
                                        maxLines = 3,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }
                            // Add divider after header row (if next line is separator)
                            if (cells.any { it.contains("可能性") || it.contains("诊断") || it.contains("说明") }) {
                                Divider(
                                    modifier = Modifier.padding(vertical = 2.dp),
                                    color = Color.LightGray
                                )
                            }
                        }
                    }
                }
                // Header level 3: ### text or ### **text**
                trimmedLine.startsWith("### ") -> {
                    val headerText = trimmedLine.removePrefix("### ").let { text ->
                        // Remove ** markers if present
                        text.removeSurrounding("**", "**").let { inner ->
                            if (inner != text) inner else text
                        }
                    }
                    Text(
                        text = headerText,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)
                    )
                }
                // Header level 2: ## text or ## **text**
                trimmedLine.startsWith("## ") -> {
                    val headerText = trimmedLine.removePrefix("## ").let { text ->
                        text.removeSurrounding("**", "**").let { inner ->
                            if (inner != text) inner else text
                        }
                    }
                    Text(
                        text = headerText,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(top = 12.dp, bottom = 4.dp)
                    )
                }
                // Header level 1: # text or # **text**
                trimmedLine.startsWith("# ") -> {
                    val headerText = trimmedLine.removePrefix("# ").let { text ->
                        text.removeSurrounding("**", "**").let { inner ->
                            if (inner != text) inner else text
                        }
                    }
                    Text(
                        text = headerText,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(top = 16.dp, bottom = 4.dp)
                    )
                }
                // List item: * text or - text
                trimmedLine.startsWith("* ") || trimmedLine.startsWith("- ") -> {
                    Row(modifier = Modifier.padding(start = 8.dp, top = 2.dp, bottom = 2.dp)) {
                        Text("• ", style = MaterialTheme.typography.bodyMedium)
                        MarkdownText(
                            text = trimmedLine.removePrefix("* ").removePrefix("- "),
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
                // Numbered list item: 1. text or 2. text
                trimmedLine.matches(Regex("^\\d+\\.\\s+.+")) -> {
                    val number = trimmedLine.substringBefore(". ")
                    val text = trimmedLine.substringAfter(". ")
                    Row(modifier = Modifier.padding(start = 8.dp, top = 2.dp, bottom = 2.dp)) {
                        Text("$number. ", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
                        MarkdownText(
                            text = text,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
                // Horizontal rule: --- or ***
                trimmedLine == "---" || trimmedLine == "***" || trimmedLine == "___" -> {
                    Divider(modifier = Modifier.padding(vertical = 8.dp))
                }
                // Empty line
                trimmedLine.isBlank() -> {
                    Spacer(modifier = Modifier.height(4.dp))
                }
                // Regular paragraph
                else -> {
                    MarkdownText(
                        text = line,
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier.padding(vertical = 2.dp)
                    )
                }
            }
        }
    }
}

// Helper function to get file name from URI
fun getFileName(context: android.content.Context, uri: Uri): String? {
    var result: String? = null
    if (uri.scheme == "content") {
        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                val columnIndex = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                if (columnIndex >= 0) {
                    result = cursor.getString(columnIndex)
                }
            }
        }
    }
    if (result == null) {
        result = uri.path?.substringAfterLast('/')
    }
    return result
}

// Helper function to format file size
fun formatFileSize(size: Long): String {
    return when {
        size < 1024 -> "${size}B"
        size < 1024 * 1024 -> "${size / 1024}KB"
        else -> "${size / (1024 * 1024)}MB"
    }
}
