package com.medicareai.patient.di

import android.content.Context
import com.medicareai.patient.data.api.MediCareApiClient
import com.medicareai.patient.data.local.TokenManager
import com.medicareai.patient.data.repository.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideTokenManager(@ApplicationContext context: Context): TokenManager {
        return TokenManager(context)
    }

    @Provides
    @Singleton
    fun provideApiClient(tokenManager: TokenManager): MediCareApiClient {
        return MediCareApiClient(tokenManager)
    }

    @Provides
    @Singleton
    fun provideAuthRepository(apiClient: MediCareApiClient, tokenManager: TokenManager): AuthRepository {
        return AuthRepository(apiClient, tokenManager)
    }
    
    @Provides
    @Singleton
    fun providePatientRepository(apiClient: MediCareApiClient): PatientRepository {
        return PatientRepository(apiClient)
    }
    
    @Provides
    @Singleton
    fun provideMedicalCaseRepository(apiClient: MediCareApiClient): MedicalCaseRepository {
        return MedicalCaseRepository(apiClient)
    }
    
    @Provides
    @Singleton
    fun provideAIDiagnosisRepository(apiClient: MediCareApiClient): AIDiagnosisRepository {
        return AIDiagnosisRepository(apiClient)
    }
    
    @Provides
    @Singleton
    fun provideDoctorRepository(apiClient: MediCareApiClient): DoctorRepository {
        return DoctorRepository(apiClient)
    }
    
    @Provides
    @Singleton
    fun provideDocumentRepository(apiClient: MediCareApiClient): DocumentRepository {
        return DocumentRepository(apiClient)
    }
}
