function objectToQueryString(obj) {
  const queryParams = new URLSearchParams()

  // Iterate through the object properties and add them to the URLSearchParams object
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      queryParams.append(key, obj[key])
    }
  }

  // Convert the URLSearchParams object to a string
  return queryParams.toString()
}

export class HttpService {
  private root: string

  constructor(root: string) {
    this.root = root
  }

  async get(url: string, queryParams = {}) {
    const queryStr = objectToQueryString(queryParams)
    const response = await fetch(`${this.root}/${url}?${queryStr}`)
    return await response.json()
  }

  async post(url: string, body = {}) {
    const response = await fetch(`${this.root}/${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    return await response.json()
  }
}
