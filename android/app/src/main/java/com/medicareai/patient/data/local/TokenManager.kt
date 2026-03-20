package com.medicareai.patient.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

class TokenManager(private val context: Context) {
    companion object {
        private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN_KEY = stringPreferencesKey("refresh_token")
        private val TOKEN_EXPIRES_AT_KEY = longPreferencesKey("token_expires_at")
    }

    val accessToken: Flow<String?> = context.dataStore.data
        .map { preferences ->
            preferences[ACCESS_TOKEN_KEY]
        }

    val refreshToken: Flow<String?> = context.dataStore.data
        .map { preferences ->
            preferences[REFRESH_TOKEN_KEY]
        }

    val tokenExpiresAt: Flow<Long?> = context.dataStore.data
        .map { preferences ->
            preferences[TOKEN_EXPIRES_AT_KEY]
        }

    suspend fun saveTokens(accessToken: String, refreshToken: String, expiresIn: Long = 1800) {
        val expiresAt = System.currentTimeMillis() + (expiresIn * 1000)
        context.dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = accessToken
            preferences[REFRESH_TOKEN_KEY] = refreshToken
            preferences[TOKEN_EXPIRES_AT_KEY] = expiresAt
        }
    }

    suspend fun saveAccessToken(accessToken: String, expiresIn: Long = 1800) {
        val expiresAt = System.currentTimeMillis() + (expiresIn * 1000)
        context.dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = accessToken
            preferences[TOKEN_EXPIRES_AT_KEY] = expiresAt
        }
    }

    suspend fun getRefreshToken(): String? {
        return refreshToken.first()
    }

    suspend fun getAccessToken(): String? {
        return accessToken.first()
    }

    suspend fun clearTokens() {
        context.dataStore.edit { preferences ->
            preferences.remove(ACCESS_TOKEN_KEY)
            preferences.remove(REFRESH_TOKEN_KEY)
            preferences.remove(TOKEN_EXPIRES_AT_KEY)
        }
    }

    suspend fun isTokenExpired(): Boolean {
        val expiresAt = tokenExpiresAt.first() ?: return true
        return System.currentTimeMillis() >= expiresAt
    }

    suspend fun shouldRefreshToken(): Boolean {
        val expiresAt = tokenExpiresAt.first() ?: return true
        val fiveMinutesInMillis = 5 * 60 * 1000
        return System.currentTimeMillis() >= (expiresAt - fiveMinutesInMillis)
    }
}
