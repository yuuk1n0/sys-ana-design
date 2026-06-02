import { lStorage } from '@/utils'

const TOKEN_CODE = 'access_token'

export function getToken() {
  return lStorage.get(TOKEN_CODE)
}

export function setToken(token) {
  lStorage.set(TOKEN_CODE, token)
}

export function removeToken() {
  lStorage.remove(TOKEN_CODE)
}
