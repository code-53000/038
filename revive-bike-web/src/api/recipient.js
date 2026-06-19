import request from '@/utils/request'

export const createRecipientApi = (data) => {
  return request({
    url: '/recipients',
    method: 'post',
    data
  })
}

export const getRecipientsApi = (params) => {
  return request({
    url: '/recipients',
    method: 'get',
    params
  })
}

export const getRecipientDetailApi = (id) => {
  return request({
    url: `/recipients/${id}`,
    method: 'get'
  })
}

export const approveRecipientApi = (id) => {
  return request({
    url: `/recipients/${id}/approve`,
    method: 'post'
  })
}

export const rejectRecipientApi = (id, reviewNotes) => {
  return request({
    url: `/recipients/${id}/reject`,
    method: 'post',
    params: { review_notes: reviewNotes }
  })
}

export const createMatchApi = (data) => {
  return request({
    url: '/matches',
    method: 'post',
    data
  })
}

export const getMatchesApi = (params) => {
  return request({
    url: '/matches',
    method: 'get',
    params
  })
}

export const getMatchDetailApi = (id) => {
  return request({
    url: `/matches/${id}`,
    method: 'get'
  })
}

export const deliverMatchApi = (id) => {
  return request({
    url: `/matches/${id}/deliver`,
    method: 'post'
  })
}
