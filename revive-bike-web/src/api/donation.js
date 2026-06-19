import request from '@/utils/request'

export const createDonationApi = (data) => {
  return request({
    url: '/donations',
    method: 'post',
    data
  })
}

export const getDonationsApi = (params) => {
  return request({
    url: '/donations',
    method: 'get',
    params
  })
}

export const getDonationDetailApi = (id) => {
  return request({
    url: `/donations/${id}`,
    method: 'get'
  })
}

export const getDonationHistoryApi = (id) => {
  return request({
    url: `/donations/${id}/history`,
    method: 'get'
  })
}

export const schedulePickupApi = (donationId, data) => {
  return request({
    url: `/donations/${donationId}/schedule-pickup`,
    method: 'post',
    data
  })
}

export const getPickupsApi = (params) => {
  return request({
    url: '/donations/pickups/list',
    method: 'get',
    params
  })
}

export const assignPickupApi = (pickupId) => {
  return request({
    url: `/donations/pickups/${pickupId}/assign`,
    method: 'post'
  })
}

export const completePickupApi = (pickupId, data) => {
  return request({
    url: `/donations/pickups/${pickupId}/complete`,
    method: 'post',
    data
  })
}

export const traceDonationApi = (donationId) => {
  return request({
    url: `/trace/${donationId}`,
    method: 'get'
  })
}
