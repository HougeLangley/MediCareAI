import React, { useState, useEffect } from 'react';
import { FormControl, InputLabel, Select, MenuItem, Grid, TextField } from '@mui/material';
import { provinces, getCitiesByProvince, getDistrictsByCity, formatFullAddress } from '../../data/chinaRegions';

interface AddressSelectProps {
  value: {
    province: string;
    city: string;
    district: string;
    detail: string;
  };
  onChange: (address: {
    province: string;
    city: string;
    district: string;
    detail: string;
    fullAddress: string;
  }) => void;
  disabled?: boolean;
  required?: boolean;
}

export const AddressSelect: React.FC<AddressSelectProps> = ({
  value,
  onChange,
  disabled = false,
  required = false,
}) => {
  const [province, setProvince] = useState(value.province || '');
  const [city, setCity] = useState(value.city || '');
  const [district, setDistrict] = useState(value.district || '');
  const [detail, setDetail] = useState(value.detail || '');

  const cities = province ? getCitiesByProvince(province) : [];
  const districts = province && city ? getDistrictsByCity(province, city) : [];

  // 当外部value变化时更新内部状态
  useEffect(() => {
    setProvince(value.province || '');
    setCity(value.city || '');
    setDistrict(value.district || '');
    setDetail(value.detail || '');
  }, [value.province, value.city, value.district, value.detail]);

  // 通知父组件地址变化
  const notifyChange = (
    newProvince: string,
    newCity: string,
    newDistrict: string,
    newDetail: string
  ) => {
    const fullAddress = formatFullAddress(newProvince, newCity, newDistrict, newDetail);
    onChange({
      province: newProvince,
      city: newCity,
      district: newDistrict,
      detail: newDetail,
      fullAddress,
    });
  };

  const handleProvinceChange = (e: React.ChangeEvent<{ value: unknown }>) => {
    const newProvince = e.target.value as string;
    setProvince(newProvince);
    setCity('');
    setDistrict('');
    notifyChange(newProvince, '', '', detail);
  };

  const handleCityChange = (e: React.ChangeEvent<{ value: unknown }>) => {
    const newCity = e.target.value as string;
    setCity(newCity);
    setDistrict('');
    notifyChange(province, newCity, '', detail);
  };

  const handleDistrictChange = (e: React.ChangeEvent<{ value: unknown }>) => {
    const newDistrict = e.target.value as string;
    setDistrict(newDistrict);
    notifyChange(province, city, newDistrict, detail);
  };

  const handleDetailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDetail = e.target.value;
    setDetail(newDetail);
    notifyChange(province, city, district, newDetail);
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={4}>
        <FormControl fullWidth required={required} disabled={disabled}>
          <InputLabel>省份</InputLabel>
          <Select value={province} onChange={handleProvinceChange} label="省份">
            <MenuItem value="">
              <em>请选择省份</em>
            </MenuItem>
            {provinces.map((prov) => (
              <MenuItem key={prov.code} value={prov.name}>
                {prov.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} sm={4}>
        <FormControl fullWidth required={required} disabled={disabled || !province}>
          <InputLabel>城市</InputLabel>
          <Select value={city} onChange={handleCityChange} label="城市">
            <MenuItem value="">
              <em>请选择城市</em>
            </MenuItem>
            {cities.map((c) => (
              <MenuItem key={c.code} value={c.name}>
                {c.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} sm={4}>
        <FormControl fullWidth required={required} disabled={disabled || !city}>
          <InputLabel>区县</InputLabel>
          <Select value={district} onChange={handleDistrictChange} label="区县">
            <MenuItem value="">
              <em>请选择区县</em>
            </MenuItem>
            {districts.map((d) => (
              <MenuItem key={d.code} value={d.name}>
                {d.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="详细地址"
          placeholder="请输入街道、门牌号等详细地址"
          value={detail}
          onChange={handleDetailChange}
          disabled={disabled}
          required={required}
          multiline
          rows={2}
        />
      </Grid>
    </Grid>
  );
};

export default AddressSelect;
