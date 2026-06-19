import request from '@/utils/request'

export const getPartsApi = (params) => {
  return request({
    url: '/parts',
    method: 'get',
    params
  })
}

export const getPartDetailApi = (id) => {
  return request({
    url: `/parts/${id}`,
    method: 'get'
  })
}

export const createPartApi = (data) => {
  return request({
    url: '/parts',
    method: 'post',
    data
  })
}

export const updatePartApi = (id, data) => {
  return request({
    url: `/parts/${id}`,
    method: 'put',
    data
  })
}

export const deletePartApi = (id) => {
  return request({
    url: `/parts/${id}`,
    method: 'delete'
  })
}
