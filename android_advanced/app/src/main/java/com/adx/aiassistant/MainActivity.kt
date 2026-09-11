package com.adx.aiassistant

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

private val AdxNavy = Color(0xFF08111F)
private val AdxPanel = Color(0xFF111E31)
private val AdxText = Color(0xFFEAF2FF)
private val AdxMuted = Color(0xFF9BAAC0)
private val AdxBlue = Color(0xFF6CB6FF)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { AdxApp(getSharedPreferences("adx", Context.MODE_PRIVATE)) }
    }
}

@Composable
private fun AdxApp(prefs: SharedPreferences) {
    var screen by remember { mutableStateOf("home") }
    MaterialTheme(colorScheme = darkColorScheme(primary = AdxBlue, background = AdxNavy, surface = AdxPanel)) {
        when (screen) {
            "chat" -> ChatScreen(prefs) { screen = "home" }
            "settings" -> SettingsScreen(prefs) { screen = "home" }
            "memory" -> MemoryScreen(prefs) { screen = "home" }
            "capabilities" -> CapabilitiesScreen { screen = "home" }
            else -> HomeScreen(
                onChat = { screen = "chat" },
                onSettings = { screen = "settings" },
                onMemory = { screen = "memory" },
                onCapabilities = { screen = "capabilities" }
            )
        }
    }
}

@Composable
private fun HomeScreen(onChat: () -> Unit, onSettings: () -> Unit, onMemory: () -> Unit, onCapabilities: () -> Unit) {
    Scaffold(containerColor = AdxNavy) { pad ->
        LazyColumn(Modifier.fillMaxSize().padding(pad).padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            item {
                Text("ADX", color = AdxBlue, style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold)
                Text("AI Assistant • Advanced Android", color = AdxText, style = MaterialTheme.typography.headlineSmall)
                Text("Voice, AI chat, memory, permissions and automation foundations.", color = AdxMuted)
            }
            item { ActionCard("Chat with ADX", "Ask questions using your configured AI provider.", Icons.Default.Chat, onChat) }
            item { ActionCard("Capabilities", "Calls, SMS, WhatsApp, notifications, accessibility, documents, coding and more.", Icons.Default.Tune, onCapabilities) }
            item { ActionCard("Memory", "Store local notes and preferences for ADX.", Icons.Default.Memory, onMemory) }
            item { ActionCard("Settings", "API provider, permissions and integrations.", Icons.Default.Settings, onSettings) }
        }
    }
}

@Composable
private fun ActionCard(title: String, desc: String, icon: androidx.compose.ui.graphics.vector.ImageVector, onClick: () -> Unit) {
    Card(Modifier.fillMaxWidth().clickable(onClick = onClick), colors = CardDefaults.cardColors(containerColor = AdxPanel)) {
        Row(Modifier.padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, title, tint = AdxBlue, modifier = Modifier.size(30.dp))
            Spacer(Modifier.width(16.dp))
            Column { Text(title, color = AdxText, fontWeight = FontWeight.Bold); Text(desc, color = AdxMuted) }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ChatScreen(prefs: SharedPreferences, back: () -> Unit) {
    var input by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf("Namaste! Main ADX hoon. Settings me AI provider configure karo.") }
    var busy by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    Scaffold(containerColor = AdxNavy, topBar = { TopAppBar(title = { Text("ADX Chat") }, navigationIcon = { IconButton(back) { Icon(Icons.Default.ArrowBack, "Back") } }) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).padding(16.dp)) {
            Card(colors = CardDefaults.cardColors(containerColor = AdxPanel)) { Text(answer, color = AdxText, modifier = Modifier.padding(18.dp)) }
            Spacer(Modifier.weight(1f))
            OutlinedTextField(input, { input = it }, Modifier.fillMaxWidth(), label = { Text("Ask ADX") })
            Spacer(Modifier.height(10.dp))
            Button(enabled = input.isNotBlank() && !busy, modifier = Modifier.fillMaxWidth(), onClick = {
                val q = input.trim(); scope.launch { busy = true; answer = askAi(prefs, q) ?: "API key configure nahi hai."; busy = false }
            }) { Text(if (busy) "Thinking…" else "Send") }
        }
    }
}

private suspend fun askAi(prefs: SharedPreferences, prompt: String): String? = withContext(Dispatchers.IO) {
    val key = prefs.getString("key", "") ?: ""
    if (key.isBlank()) return@withContext null
    val endpoint = prefs.getString("endpoint", "https://api.openai.com/v1/chat/completions") ?: return@withContext null
    val model = prefs.getString("model", "gpt-4o-mini") ?: "gpt-4o-mini"
    val json = JSONObject().put("model", model).put("messages", JSONArray().put(JSONObject().put("role", "user").put("content", prompt)))
    val request = Request.Builder().url(endpoint).addHeader("Authorization", "Bearer $key").post(json.toString().toRequestBody("application/json".toMediaType())).build()
    try {
        OkHttpClient().newCall(request).execute().use { r ->
            if (!r.isSuccessful) return@withContext "AI request failed: HTTP ${r.code}"
            JSONObject(r.body?.string() ?: "{}").optJSONArray("choices")?.optJSONObject(0)?.optJSONObject("message")?.optString("content") ?: "Empty AI response"
        }
    } catch (e: Exception) { "Network/API error: ${e.message ?: "unknown"}" }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SettingsScreen(prefs: SharedPreferences, back: () -> Unit) {
    var key by remember { mutableStateOf(prefs.getString("key", "") ?: "") }
    var endpoint by remember { mutableStateOf(prefs.getString("endpoint", "https://api.openai.com/v1/chat/completions") ?: "") }
    var model by remember { mutableStateOf(prefs.getString("model", "gpt-4o-mini") ?: "") }
    val context = androidx.compose.ui.platform.LocalContext.current
    val permissions = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {}
    Scaffold(containerColor = AdxNavy, topBar = { TopAppBar(title = { Text("Settings") }, navigationIcon = { IconButton(back) { Icon(Icons.Default.ArrowBack, "Back") } }) }) { pad ->
        LazyColumn(Modifier.fillMaxSize().padding(pad).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            item { Text("AI Provider", color = AdxText, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold) }
            item { OutlinedTextField(key, { key = it }, Modifier.fillMaxWidth(), label = { Text("API key") }) }
            item { OutlinedTextField(endpoint, { endpoint = it }, Modifier.fillMaxWidth(), label = { Text("OpenAI-compatible endpoint") }) }
            item { OutlinedTextField(model, { model = it }, Modifier.fillMaxWidth(), label = { Text("Model") }) }
            item { Button(Modifier.fillMaxWidth(), onClick = { prefs.edit().putString("key", key).putString("endpoint", endpoint).putString("model", model).apply(); Toast.makeText(context, "Saved", Toast.LENGTH_SHORT).show() }) { Text("Save AI settings") } }
            item { Text("Permissions & Integrations", color = AdxText, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold) }
            item { Button(Modifier.fillMaxWidth(), onClick = { permissions.launch(arrayOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.CAMERA, Manifest.permission.POST_NOTIFICATIONS)) }) { Text("Request permissions") } }
            item { Button(Modifier.fillMaxWidth(), onClick = { context.startActivity(Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")) }) { Text("Open Notification Access") } }
            item { Button(Modifier.fillMaxWidth(), onClick = { context.startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }) { Text("Open Accessibility / Automation") } }
            item { Text("Security: production apps should use short-lived tokens or a secure backend instead of a long-lived API key on-device.", color = AdxMuted) }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MemoryScreen(prefs: SharedPreferences, back: () -> Unit) {
    var memory by remember { mutableStateOf(prefs.getString("memory", "") ?: "") }
    Scaffold(containerColor = AdxNavy, topBar = { TopAppBar(title = { Text("ADX Memory") }, navigationIcon = { IconButton(back) { Icon(Icons.Default.ArrowBack, "Back") } }) }) { pad ->
        Column(Modifier.fillMaxSize().padding(pad).padding(16.dp)) {
            Text("Local memory", color = AdxText, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Text("Saved only on this device.", color = AdxMuted)
            Spacer(Modifier.height(16.dp))
            OutlinedTextField(memory, { memory = it }, Modifier.fillMaxWidth().height(180.dp), label = { Text("What should ADX remember?") })
            Spacer(Modifier.height(10.dp))
            Button(Modifier.fillMaxWidth(), onClick = { prefs.edit().putString("memory", memory).apply() }) { Text("Save memory") }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CapabilitiesScreen(back: () -> Unit) {
    val caps = listOf("Voice & AI chat", "Calls / SMS / Contacts", "WhatsApp integration point", "Accessibility phone automation", "Notifications", "Camera & screen permission flows", "Alarms & reminders", "Music & video", "Deep research API point", "Coding & websites", "Documents & email", "Markets API point", "PC ↔ Phone connector", "Smart home connector", "Voice Guardian foundation", "Background agents / WorkManager", "Skills & macros", "Social media connector", "Persistent local memory", "Multiple personality slots")
    Scaffold(containerColor = AdxNavy, topBar = { TopAppBar(title = { Text("ADX Capabilities") }, navigationIcon = { IconButton(back) { Icon(Icons.Default.ArrowBack, "Back") } }) }) { pad ->
        LazyColumn(Modifier.fillMaxSize().padding(pad).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            item { Text("Advanced feature roadmap", color = AdxText, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold) }
            items(caps.size) { i -> Card(colors = CardDefaults.cardColors(containerColor = AdxPanel)) { Text("✓  ${caps[i]}", color = AdxText, modifier = Modifier.padding(14.dp)) } }
        }
    }
}
