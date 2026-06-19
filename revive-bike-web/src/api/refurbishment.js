import request from '@/utils/request'

export const getBikesApi = (params) => {
  return request({
    url: '/bikes',
    method: 'get',
    params
  })
}

export const getBikeDetailApi = (id) => {
  return request({
    url: `/bikes/${id}`,
    method: 'get'
  })
}

export const createRefurbishmentApi = (data) => {
  return request({
    url: '/refurbishments',
    method: 'post',
    data
  })
}

export const getRefurbishmentsApi = (params) => {
  return request({
    url: '/refurbishments',
    method: 'get',
    params
  })
}

export const getRefurbishmentDetailApi = (id) => {
  return request({
    url: `/refurbishments/${id}`,
    method: 'get'
  })
}

export const updateRefurbishmentApi = (id, data) => {
  return request({
    url: `/refurbishments/${id}`,
    method: 'put',
    data
  })
}

export const completeRefurbishmentApi = (id) => {
  return request({
    url: `/refurbishments/${id}/complete`,
    method: 'post'
  })
}

export const createPartUsageApi = (data) => {
  return request({
    url: '/part-usages',
    method: 'post',
    data
  })
}

export const getBikePartUsagesApi = (bikeId) => {
  return request({
    url: `/bikes/${bikeId}/part-usages`,
    method: 'get'
  })
}
