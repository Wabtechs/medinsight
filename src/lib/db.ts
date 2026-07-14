import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import * as schema from './schema'

let _db: ReturnType<typeof drizzle<typeof schema>> | null = null

function createDb() {
  const url = process.env.DATABASE_URL
  if (!url) throw new Error('DATABASE_URL is not set')
  return drizzle(neon(url), { schema })
}

export function getDb() {
  if (!_db) _db = createDb()
  return _db
}

type Db = ReturnType<typeof getDb>

export const db: Db = new Proxy({} as Db, {
  get(_, prop) {
    const target = getDb()
    const val = (target as Record<string | symbol, unknown>)[prop]
    if (typeof val === 'function') {
      return val.bind(target)
    }
    return val
  },
})
